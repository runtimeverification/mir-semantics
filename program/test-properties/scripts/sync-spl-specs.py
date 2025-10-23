#!/usr/bin/env python3
"""Rebuild the Solana SPL entrypoint harnesses from the Pinocchio source.

Flow (see sections below):
  main
    ├─ extract_test_functions
    ├─ assemble_sections (per configured output)
    │    └─ transform_harness
    │          ├─ comment_out_lines / apply_replacements
    │          ├─ infer_instruction_types / resolve_instruction_types
    │          └─ prepare_account_metadata / render_default_match_arm
    └─ render_template

Review guide:
* Focus on the pipeline functions and the conversion helpers around
  `transform_harness`; they directly define how p-token harnesses become SPL
  harnesses.
* Parsing helpers, configuration dataclasses, and other scaffolding are support
  code (flagged below) and usually need less scrutiny.
"""

from __future__ import annotations

import json
import re
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "program/test-properties/scripts"
CONFIG_PATH = SCRIPTS_DIR / "sync_spl_specs_config.json"

MATCH_ARM_TEMPLATE = """        // {discriminator} - {title}
        {discriminator} => {{
            {function_name}(
                program_id,
                {account_line},{account_line_comment}
                {instruction_arg},
            )
        }}"""


# Pipeline --------------------------------------------------------------------
def main() -> None:
    """Entry point: load config, run transforms, and write the SPL harness file."""
    config = SyncConfig.load(CONFIG_PATH)
    source_text = config.source.read_text()
    functions = extract_test_functions(source_text)
    for output_cfg in config.outputs:
        template_text = output_cfg.template.read_text()
        sections = assemble_sections(output_cfg, functions)
        rendered = render_template(template_text, sections, output_cfg)
        output_cfg.target.write_text(rendered)

        summarize_differences(output_cfg)
        print(
            "Wrote "
            f"{output_cfg.target.relative_to(REPO_ROOT)} "
            "from pinocchio transformations."
        )


def assemble_sections(output_cfg: OutputConfig, functions: Dict[str, str]) -> Dict[str, List[str]]:
    """Apply harness transforms and collect the generated bodies and match arms."""
    harnesses: List[str] = []
    match_arms: List[str] = []
    covered_functions: set[str] = set()

    for func_cfg in output_cfg.functions:
        source_snippet = functions.get(func_cfg.name)
        if source_snippet is None:
            raise KeyError(f"Missing function `{func_cfg.name}` in source file")

        harness, account_expr, account_comment = transform_harness(source_snippet, func_cfg)

        # For rvo output, use full accounts slice in calls (avoid first_chunk const generic)
        account_expr_out = account_expr
        if output_cfg.name == "entrypoint_rvo":
            account_expr_out = "accounts"

        # Match-arm selection via overrides (skip/custom/default)
        override = output_cfg.overrides.get(func_cfg.name, {}) if output_cfg.overrides else {}
        if override.get("skip_match_arm"):
            # Still generate harness, but do not dispatch directly to it.
            pass
        elif override.get("custom_match_arm_template"):
            rendered, covered = render_custom_match_arm(
                func_cfg,
                account_expr_out,
                account_comment,
                override,
            )
            match_arms.append(rendered)
            covered_functions.update(covered)
        else:
            instruction_mode = override.get("instruction_arg_mode", "chunk")
            match_arms.append(
                render_default_match_arm(
                    func_cfg,
                    account_expr_out,
                    account_comment,
                    instruction_mode,
                )
            )
            covered_functions.add(func_cfg.name)
        # For rvo output, relax accounts parameter type from fixed-size array to slice
        if output_cfg.name == "entrypoint_rvo":
            pattern = re.compile(r"^(\s*)accounts:\s*&\[AccountInfo;\s*(\d+)\s*\],", flags=re.MULTILINE)
            harness_relaxed = pattern.sub(
                lambda m: f"{m.group(1)}accounts: &[AccountInfo], // CHANGE P-Token: accounts: &[AccountInfo; {m.group(2)}]",
                harness,
            )
            harnesses.append(harness_relaxed)
        else:
            harnesses.append(harness)
    # Attach coverage metadata for later summary
    output_cfg.covered_functions = covered_functions  # type: ignore[attr-defined]

    return {
        "match_arms": match_arms,
        "harnesses": harnesses,
    }


def render_template(template_text: str, sections: Dict[str, List[str]], output_cfg: OutputConfig) -> str:
    """Inject each rendered section into the template according to configured placeholders."""
    rendered = template_text
    for name, placeholder in output_cfg.placeholders.items():
        items = sections.get(name, [])
        rule = output_cfg.section_rules[name]
        if not items:
            replacement = placeholder
        else:
            chunk = rule.separator.join(items)
            if rule.trailing_newline:
                chunk += "\n"
            replacement = chunk
        rendered = replace_placeholder(rendered, placeholder, replacement)
    return rendered.rstrip("\n") + "\n"


def summarize_differences(output_cfg: OutputConfig) -> None:
    """Log a lightweight summary of the configured transformations."""
    print(f"Configured transforms for {output_cfg.name}:")
    for func_cfg in output_cfg.functions:
        harness = func_cfg.harness
        print(
            f" - {func_cfg.name}: "
            f"{len(harness.comment_out)} comment-out, "
            f"{len(harness.replacements)} replacements"
        )
    covered = getattr(output_cfg, "covered_functions", set())
    all_funcs = {f.name for f in output_cfg.functions}
    uncovered = sorted(all_funcs - set(covered))
    if uncovered:
        print("Uncovered (not dispatched) in", output_cfg.name, ":", ", ".join(uncovered))
    else:
        print("All configured harnesses are dispatched in", output_cfg.name)


# Conversion helpers (REVIEW FOCUS) -------------------------------------------
def transform_harness(snippet: str, func_cfg: "FunctionConfig") -> tuple[str, str, str]:
    """Rewrite a single p-token harness into the SPL form and return match-arm metadata."""
    cfg = func_cfg.harness
    payload_type, instruction_data_type = resolve_instruction_types(snippet, func_cfg.name)

    header_block, body_block = _split_snippet_blocks(snippet, func_cfg.name)
    doc_lines, attr_lines, original_account_line = _collect_header_metadata(header_block)
    # Rewrite documentation comments to describe full instruction layout
    # with explicit discriminator at instruction_data[0], and shift any
    # existing payload-relative indices by +1 to match full-instruction view.
    if doc_lines:
        doc_lines = _rewrite_doc_comments(doc_lines, func_cfg)
    if original_account_line is None:
        raise ValueError(
            f"Unable to infer accounts parameter for `{func_cfg.name}`; ensure the source harness contains it or add a replacement."
        )

    account_line, account_expr, account_comment = _derive_account_metadata(
        original_account_line,
        cfg,
    )
    signature = _build_signature(func_cfg, account_line, instruction_data_type)

    leading_uses, body_lines = _prepare_body_lines(body_block, cfg, func_cfg.name)
    prologue = _build_prologue(func_cfg, payload_type)
    epilogue = _build_epilogue()

    harness_text = _render_harness(
        doc_lines,
        attr_lines,
        signature,
        leading_uses,
        prologue,
        body_lines,
        epilogue,
    )
    return harness_text, account_expr, account_comment


def _rewrite_doc_comments(doc_lines: List[str], func_cfg: "FunctionConfig") -> List[str]:
    """Return doc lines rewritten to:
    - Insert a line for program_id.
    - Insert a line for instruction_data[0] as the discriminator with title.
    - Shift any instruction_data indices in existing lines by +1
      (e.g., [0] -> [1], [1..9] -> [2..10], [..] -> [1..]).
    The goal is to make docs describe the full wire format rather than the
    payload-only view used in p-token harnesses.
    """

    def bump_range(expr: str) -> str:
        s = expr.strip()
        if not s:
            return s
        # ..
        if s == "..":
            return "1.."
        # a..b
        m = re.fullmatch(r"(\d+)\.\.(\d+)", s)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            return f"{a + 1}..{b + 1}"
        # a..
        m = re.fullmatch(r"(\d+)\.\.", s)
        if m:
            a = int(m.group(1))
            return f"{a + 1}.."
        # ..b
        m = re.fullmatch(r"\.\.(\d+)", s)
        if m:
            b = int(m.group(1))
            return f"1..{b + 1}"
        # single number
        m = re.fullmatch(r"(\d+)", s)
        if m:
            return str(int(m.group(1)) + 1)
        # Anything else, leave as-is
        return s

    instr_pat = re.compile(r"instruction_data\[\s*([^\]]*?)\s*\]")

    # Transform existing doc lines: bump indices in any instruction_data[..]
    transformed: List[str] = []
    for line in doc_lines:
        if "instruction_data[" in line:
            def _repl(m: re.Match) -> str:
                inner = m.group(1)
                bumped = bump_range(inner)
                return f"instruction_data[{bumped}]"

            new_line = instr_pat.sub(_repl, line)
            transformed.append(new_line)
        else:
            transformed.append(line)

    # Build the inserted lines
    prog_line = "/// program_id // Token Program ID"
    title = to_title(func_cfg.name)
    disc_line = f"/// instruction_data[0] // Discriminator {func_cfg.discriminator} ({title})"

    # Insert program_id at the very top, insert discriminator right before
    # the first instruction_data doc line (if any), else append at the end.
    first_instr_idx = next((i for i, l in enumerate(transformed) if "instruction_data[" in l), None)

    out: List[str] = []
    out.append(prog_line)
    if first_instr_idx is None:
        out.extend(transformed)
        out.append(disc_line)
    else:
        out.extend(transformed[:first_instr_idx])
        out.append(disc_line)
        out.extend(transformed[first_instr_idx:])

    return out


def _split_snippet_blocks(snippet: str, func_name: str) -> tuple[str, str]:
    """Return the header (without brace) and body block (without closing brace)."""
    brace_start = snippet.find("{")
    if brace_start == -1:
        raise ValueError(f"Malformed function snippet for {func_name}")
    body_block = snippet[brace_start + 1 :]
    if "}" not in body_block:
        raise ValueError(f"Function body missing closing brace for {func_name}")
    body_block, _closing = body_block.rsplit("}", 1)
    header_block = snippet[:brace_start].rstrip()
    return header_block, body_block


def _collect_header_metadata(header_block: str) -> tuple[List[str], List[str], str | None]:
    """Extract doc attributes and the accounts line from the header block."""
    doc_lines: List[str] = []
    attr_lines: List[str] = []
    original_account_line: str | None = None

    for line in header_block.splitlines():
        stripped = line.strip()
        if stripped.startswith("///"):
            doc_lines.append(stripped)
        elif stripped.startswith("#["):
            attr_lines.append(stripped)
        elif original_account_line is None and stripped.startswith("accounts:"):
            original_account_line = stripped

    if original_account_line is None:
        account_match = re.search(r"(accounts\s*:\s*[^,\)]+)(,|\))", header_block)
        if account_match:
            account_text = account_match.group(1).strip()
            if account_match.group(2) == ",":
                account_text += ","
            original_account_line = account_text

    return doc_lines, attr_lines, original_account_line


def _derive_account_metadata(
    original_account_line: str,
    cfg: "HarnessConfig",
) -> tuple[str, str, str]:
    """Apply literal replacements to the accounts line and build match-arm metadata."""
    candidate = original_account_line
    for repl in cfg.replacements:
        if repl.is_regex or repl.literal_from is None:
            continue
        if repl.literal_from in candidate:
            candidate = candidate.replace(repl.literal_from, repl.replacement)

    return prepare_account_metadata(original_account_line, candidate)


def _build_signature(
    func_cfg: "FunctionConfig",
    account_line: str,
    instruction_data_type: str,
) -> str:
    """Construct the harness function signature."""
    lines = [
        f"fn {func_cfg.name}(",
        "    program_id: &Pubkey,",
        f"    {account_line}",
        f"    instruction_data: {instruction_data_type},",
        ") -> ProgramResult {",
    ]
    return "\n".join(lines)


def _prepare_body_lines(
    body_block: str,
    cfg: "HarnessConfig",
    func_name: str,
) -> tuple[List[str], List[str]]:
    """Apply configured transforms to the harness body and split out leading `use` lines."""
    body = textwrap.dedent(body_block.rstrip())
    body = comment_out_lines(body, cfg.comment_out)
    body = apply_replacements(body, cfg.replacements)

    # Built-in normalizations that are hard to encode safely in JSON regex strings:
    # 1) get_mint(...).decimals  -> get_mint(...).decimals()
    body = re.sub(r"get_mint\(([^)]*)\)\.decimals\b(?!\()", r"get_mint(\1).decimals()", body)

    # 2) Compare Pubkey to instruction slices as bytes: append .as_ref() on unwrap
    #    assert_eq!(get_mint(&accounts[i]).mint_authority().unwrap(), &instruction_data[a..b])
    body = re.sub(
        r"assert_eq!\(\s*get_mint\(&accounts\[(\d+)\]\)\.mint_authority\(\)\.unwrap\(\),\s*&instruction_data\[(\d+)\.\.(\d+)\]\s*\)",
        r"assert_eq!(get_mint(&accounts[\1]).mint_authority().unwrap().as_ref(), &instruction_data[\2..\3])",
        body,
    )
    #    assert_eq!(get_mint(&accounts[i]).freeze_authority().unwrap(), &instruction_data[a..b])
    body = re.sub(
        r"assert_eq!\(\s*get_mint\(&accounts\[(\d+)\]\)\.freeze_authority\(\)\.unwrap\(\),\s*&instruction_data\[(\d+)\.\.(\d+)\]\s*\)",
        r"assert_eq!(get_mint(&accounts[\1]).freeze_authority().unwrap().as_ref(), &instruction_data[\2..\3])",
        body,
    )

    # 3) Multisig accessor fixes on get_multisig(...)
    body = re.sub(
        r"get_multisig\(&accounts\[(\d+)\]\)\.signers\b(?!\()",
        r"get_multisig(&accounts[\1]).signers()",
        body,
    )
    body = re.sub(
        r"get_multisig\(&accounts\[(\d+)\]\)\.m\b(?!\()",
        r"get_multisig(&accounts[\1]).m()",
        body,
    )
    body = re.sub(
        r"get_multisig\(&accounts\[(\d+)\]\)\.n\b(?!\()",
        r"get_multisig(&accounts[\1]).n()",
        body,
    )

    # Also fix line-broken method calls like
    #   get_multisig(&accounts[i])\n                .signers\n
    body = re.sub(r"\n(\s*)\.signers(\s*)\n", r"\n\1.signers()\2\n", body)

    # 4) Replace specific Multisig::is_valid_signer_index(x) with simple bounds check 1..=11
    body = body.replace(
        "!Multisig::is_valid_signer_index((accounts.len() - 1) as u8)",
        "!((((accounts.len() - 1) as u8) >= 1) && (((accounts.len() - 1) as u8) <= 11))",
    )
    body = body.replace(
        "!Multisig::is_valid_signer_index((accounts.len() - 2) as u8)",
        "!((((accounts.len() - 2) as u8) >= 1) && (((accounts.len() - 2) as u8) <= 11))",
    )
    body = body.replace(
        "!Multisig::is_valid_signer_index(instruction_data[0])",
        "!(((instruction_data[0]) >= 1) && ((instruction_data[0]) <= 11))",
    )

    # 5) program::ID (from removed pinocchio import alias) -> crate::id()
    body = body.replace("program::ID", "crate::id()")

    # pinocchio_token_interface::native_mint::ID -> native_mint::ID (template imports spl_token_interface::native_mint)
    body = body.replace(
        "pinocchio_token_interface::native_mint::ID",
        "native_mint::ID",
    )
    # pinocchio::pubkey::PUBKEY_BYTES -> pubkey::PUBKEY_BYTES (template imports solana_pubkey as pubkey)
    body = body.replace(
        "pinocchio::pubkey::PUBKEY_BYTES",
        "pubkey::PUBKEY_BYTES",
    )
    body = body.replace(
        "solana_rent::RENT_ID",
        "solana_sysvar::rent::ID",
    )

    # 6) owner() vs instruction_data fixed-size arrays: coerce to Pubkey
    body = re.sub(
        r"assert_eq!\(\s*get_account\(&accounts\[(\d+)\]\)\.owner\(\),\s*\*instruction_data\s*\)",
        r"assert_eq!(get_account(&accounts[\1]).owner(), (*instruction_data).into())",
        body,
    )
    body = re.sub(
        r"assert_eq!\(\s*get_account\(&accounts\[(\d+)\]\)\.owner\(\),\s*instruction_data\[(\d+)\.\.(\d+)\]\s*\)",
        r"assert_eq!(get_account(&accounts[\1]).owner().as_ref(), &instruction_data[\2..\3])",
        body,
    )
    body = re.sub(
        r"assert_eq!\(\s*get_account\(&accounts\[(\d+)\]\)\.close_authority\(\)\.unwrap\(\),\s*&instruction_data\[(\d+)\.\.(\d+)\]\s*\)",
        r"assert_eq!(get_account(&accounts[\1]).close_authority().unwrap().as_ref(), &instruction_data[\2..\3])",
        body,
    )
    
    # 7) Replace unsafe amount extract helper in any harness
    body = re.sub(
        r"let amount =\s*unsafe \{ u64::from_le_bytes\(\*\(instruction_data\.as_ptr\(\) as \*const \[u8; 8\]\)\) \);",
        "let amount = u64::from_le_bytes([instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3], instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7]]);",
        body,
    )
    body = body.replace(
        "let amount =  unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };",
        "let amount = u64::from_le_bytes([instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3], instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7]]);",
    )
    body = body.replace(
        "let amount = u64::from_le_bytes(*instruction_data);",
        "let amount = u64::from_le_bytes([instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3], instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7]]);",
    )
    body = re.sub(
        r"unsafe \{ u64::from_le_bytes\(\*\(instruction_data\.as_ptr\(\) as \*const \[u8; 8\]\)\) \}",
        "u64::from_le_bytes([instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3], instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7]])",
        body,
    )

    body_lines = [line.rstrip() for line in body.splitlines()]
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()
    if not body_lines or body_lines[-1].strip() != "result":
        raise ValueError(f"Expected `{func_name}` body to end with `result`")
    body_lines.pop()
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)

    leading_uses: List[str] = []
    while body_lines and body_lines[0].strip().startswith("use "):
        leading_uses.append(body_lines.pop(0).strip())
    if body_lines and body_lines[0].strip() == "":
        body_lines.pop(0)
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)

    return leading_uses, body_lines


def _build_prologue(func_cfg: "FunctionConfig", payload_type: str) -> List[str]:
    """Return the canonical prologue emitted for every harness."""
    # Two modes:
    # - Fixed-size payload: use last_chunk() to rebind as & [u8; N]
    # - Variable-size payload (payload_type == "[u8]"): slice off discriminator
    if payload_type == "[u8]":
        return [
            "// Set discriminator and program id to concrete value",
            f"cheatcode_set_discriminator({func_cfg.discriminator}, instruction_data);",
            "cheatcode_set_program_id(program_id);",
            "",
            "// Strip discriminator so instruction data is equivalent p-token harness",
            "let instruction_data_with_discriminator = &instruction_data.clone();",
            "let instruction_data: &[u8] = &instruction_data[1..];",
            "",
        ]
    else:
        return [
            "// Set discriminator and program id to concrete value",
            f"cheatcode_set_discriminator({func_cfg.discriminator}, instruction_data);",
            "cheatcode_set_program_id(program_id);",
            "",
            "// Strip discriminator so instruction data is equivalent p-token harness",
            "let instruction_data_with_discriminator = &instruction_data.clone();",
            f"let instruction_data: &{payload_type} = instruction_data.last_chunk().unwrap();",
            "",
        ]


def _build_epilogue() -> List[str]:
    """Return the canonical epilogue emitted for every harness."""
    return [
        "// Ensure instruction_data was not mutated",
        "assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);",
        "",
    ]


def _render_harness(
    doc_lines: List[str],
    attr_lines: List[str],
    signature: str,
    leading_uses: List[str],
    prologue: List[str],
    body_lines: List[str],
    epilogue: List[str],
) -> str:
    """Assemble the final harness text with indentation and metadata."""
    output_lines: List[str] = []
    if doc_lines:
        output_lines.append("\n".join(doc_lines))
    if attr_lines:
        output_lines.append("\n".join(attr_lines))
    output_lines.append(signature)

    body_output: List[str] = []
    if leading_uses:
        body_output.extend(leading_uses)
        body_output.append("")
    body_output.extend(prologue)
    if body_lines:
        body_output.extend(body_lines)
        body_output.append("")
    body_output.extend(epilogue)
    body_output.append("result")

    indented_body = "\n".join("    " + line if line else "" for line in body_output)
    output_lines.append(indented_body)
    output_lines.append("}")
    return "\n".join(output_lines)


def comment_out_lines(text: str, patterns: Iterable[str]) -> str:
    """Return `text` with each matching line turned into a commented line while preserving indentation."""
    if not patterns:
        return text

    replacements: List[Replacement] = []
    indent_group = "(?P<indent>\\s*)"
    not_commented = "(?!//)"

    for raw in patterns:
        if raw.startswith("regex:"):
            pattern_text = raw[len("regex:") :].strip()
            compiled = re.compile(
                rf"^{indent_group}{not_commented}(?P<body>.*(?:{pattern_text}).*)$",
                flags=re.MULTILINE,
            )
        else:
            literal = re.escape(raw)
            compiled = re.compile(
                rf"^{indent_group}{not_commented}(?P<body>{literal})$",
                flags=re.MULTILINE,
            )
        replacements.append(
            Replacement(
                raw_from=raw,
                replacement=r"\g<indent>// \g<body>",
                is_regex=True,
                pattern=compiled,
            )
        )

    return apply_replacements(text, replacements)


def apply_replacements(text: str, replacements: Iterable[Replacement]) -> str:
    """Apply each configured literal or regex replacement to `text` in sequence."""
    for repl in replacements:
        if repl.is_regex and repl.pattern is not None:
            text = repl.pattern.sub(repl.replacement, text)
        elif repl.literal_from is not None:
            text = text.replace(repl.literal_from, repl.replacement)
    return text


def infer_instruction_types(snippet: str) -> tuple[str | None, str | None]:
    """Infer the payload and instruction slice types from a p-token harness signature."""
    if "{" not in snippet:
        return None, None
    header, _body = snippet.split("{", 1)
    match = re.search(r"instruction_data\s*:\s*([^,\)]+)", header, flags=re.DOTALL)
    if match is None:
        # When the original harness lacks instruction data, synthesize empty payload types.
        return "[u8; 0]", "&[u8; 1]"

    raw_type = match.group(1).strip()
    compact = re.sub(r"\s+", "", raw_type)

    array_match = re.fullmatch(r"&?\[u8;(\d+)\]", compact)
    if array_match:
        payload_len = int(array_match.group(1))
        payload_type = f"[u8; {payload_len}]"
        instruction_type = f"&[u8; {payload_len + 1}]"
        return payload_type, instruction_type
    # Variable-sized slice payload
    slice_match = re.fullmatch(r"&?\[u8\]", compact)
    if slice_match:
        payload_type = "[u8]"
        instruction_type = "&[u8]"
        return payload_type, instruction_type

    return None, None


def resolve_instruction_types(snippet: str, func_name: str) -> tuple[str, str]:
    """Resolve instruction data types or raise if the signature is not yet supported."""
    payload, instruction_type = infer_instruction_types(snippet)
    if payload is None or instruction_type is None:
        raise ValueError(
            f"Unable to infer instruction data types for `{func_name}`. "
            "Update the script to handle this signature."
        )
    return payload, instruction_type


def to_title(label: str) -> str:
    """Convert a test harness name into a human-friendly title for match-arm comments."""
    base = label
    if base.startswith("test_process_"):
        base = base[len("test_process_") :]
    if base.startswith("test_"):
        base = base[len("test_") :]
    parts = [part for part in base.split("_") if part]
    return " ".join(word.capitalize() for word in parts) or label


def render_custom_match_arm(
    func_cfg: "FunctionConfig",
    account_expr: str,
    comment_block: str,
    override: Dict,
) -> tuple[str, List[str]]:
    """Render a custom match-arm using a named template and params.

    Returns (rendered_text, covered_function_names).
    """
    template_name = override.get("custom_match_arm_template")
    params = override.get("custom_match_arm_params", {})
    covered = list(override.get("custom_match_arm_functions", []))

    disc = func_cfg.discriminator
    title = to_title(func_cfg.name)
    log_lines = [
        f"// #[cfg(feature = \"logging\")]",
        f"// msg!(\"Testing Instruction: {title}\");",
        "",
    ]
    log_block = "\n            ".join(log_lines).rstrip()

    # Helper for uniform call site
    def call_site(fn_name: str) -> str:
        return (
            f"{fn_name}(\n"
            f"                program_id,\n"
            f"                {account_expr},{comment_block}\n"
            f"                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,\n"
            f"            )"
        )

    rendered = ""
    if template_name == "route_by_len_two":
        branches = params.get("branches", [])
        if len(branches) != 2:
            raise ValueError("route_by_len_two requires exactly two branches")
        # We follow user's preference B: destructure payload and compare original thresholds (no +1)
        b1, b2 = branches[0], branches[1]
        rendered = (
            f"        // {disc} - {title}\n"
            f"        {disc} => {{\n"
            f"            {log_block}\n"
            f"            let [_d, payload @ ..] = instruction_data else {{\n"
            f"                return Err(TokenError::InvalidInstruction.into());\n"
            f"            }};\n"
            f"            match payload.len() {{\n"
            f"                x if {b1['min_payload_len']} <= x => {{\n"
            f"                    {call_site(b1['function'])}\n"
            f"                }}\n"
            f"                x if {b2['min_payload_len']} <= x => {{\n"
            f"                    {call_site(b2['function'])}\n"
            f"                }}\n"
            f"                _ => Err(TokenError::InvalidInstruction.into()),\n"
            f"            }}\n"
            f"        }}"
        )
    elif template_name == "route_by_data_len_two":
        variants = params.get("variants", [])
        if len(variants) != 2:
            raise ValueError("route_by_data_len_two requires exactly two variants")
        v1, v2 = variants[0], variants[1]
        rendered = (
            f"        // {disc} - {title}\n"
            f"        {disc} => {{\n"
            f"            {log_block}\n"
            f"            if let Some(first_account) = accounts.first() {{\n"
            f"                match first_account.data_len() {{\n"
            f"                    {v1['when']} => {{\n"
            f"                        {call_site(v1['function'])}\n"
            f"                    }}\n"
            f"                    {v2['when']} => {{\n"
            f"                        {call_site(v2['function'])}\n"
            f"                    }}\n"
            f"                    _ => Err(TokenError::InvalidInstruction.into()),\n"
            f"                }}\n"
            f"            }} else {{\n"
            f"                Err(TokenError::InvalidInstruction.into())\n"
            f"            }}\n"
            f"        }}"
        )
    elif template_name == "route_by_data_len_three":
        variants = params.get("variants", [])
        if len(variants) != 3:
            raise ValueError("route_by_data_len_three requires exactly three variants")
        v1, v2, v3 = variants[0], variants[1], variants[2]
        rendered = (
            f"        // {disc} - {title}\n"
            f"        {disc} => {{\n"
            f"            {log_block}\n"
            f"            if let Some(acc) = accounts.first() {{\n"
            f"                match acc.data_len() {{\n"
            f"                    {v1['when']} => {{\n"
            f"                        {call_site(v1['function'])}\n"
            f"                    }}\n"
            f"                    {v2['when']} => {{\n"
            f"                        {call_site(v2['function'])}\n"
            f"                    }}\n"
            f"                    {v3['when']} => {{\n"
            f"                        {call_site(v3['function'])}\n"
            f"                    }}\n"
            f"                    _ => Err(TokenError::InvalidInstruction.into()),\n"
            f"                }}\n"
            f"            }} else {{\n"
            f"                Err(TokenError::InvalidInstruction.into())\n"
            f"            }}\n"
            f"        }}"
        )
    else:
        raise KeyError(f"Unknown custom_match_arm_template `{template_name}`")

    return rendered, covered


def prepare_account_metadata(
    original_account_line: str | None,
    candidate_line: str,
) -> tuple[str, str, str]:
    """Normalize the accounts parameter and capture the expression/comment used by the match arm."""
    stripped_candidate = candidate_line.strip()
    if not stripped_candidate:
        raise ValueError("Accounts parameter line is empty after replacements")

    code_part, _, comment_part = stripped_candidate.partition("//")
    code_part = code_part.strip()
    inline_comment = comment_part.strip().rstrip(", ")
    code_without_comma = code_part.rstrip(",")

    type_part = ""
    if ":" in code_without_comma:
        _, type_part = code_without_comma.split(":", 1)
        type_part = type_part.strip()

    if "[AccountInfo;" in type_part:
        account_expr = "accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?"
    else:
        account_expr = "accounts"

    comment_segments: List[str] = []
    orig_code_part = None
    if original_account_line is not None:
        orig_code_part_raw, _, _ = original_account_line.strip().partition("//")
        orig_code_part = orig_code_part_raw.strip().rstrip(",")

    if orig_code_part and orig_code_part != code_part:
        change_note = f"CHANGE P-Token: {orig_code_part}"
        if not (inline_comment and orig_code_part in inline_comment):
            comment_segments.append(change_note)

    if inline_comment:
        comment_segments.append(inline_comment)

    seen: set[str] = set()
    unique_comments: List[str] = []
    for segment in comment_segments:
        if segment and segment not in seen:
            seen.add(segment)
            unique_comments.append(segment)

    comment_suffix = ""
    if unique_comments:
        comment_suffix = " // " + "; ".join(unique_comments)

    rebuilt_line = code_without_comma
    if not rebuilt_line.endswith(","):
        rebuilt_line += ","

    if inline_comment:
        rebuilt_line = f"{rebuilt_line} // {inline_comment}"

    return rebuilt_line, account_expr, comment_suffix


def render_default_match_arm(
    func_cfg: "FunctionConfig",
    account_expr: str,
    comment_block: str,
    instruction_arg_mode: str = "chunk",
) -> str:
    """Render the SPL dispatcher branch for a transformed harness.

    instruction_arg_mode: "chunk" to pass first_chunk(); "full" to pass instruction_data slice.
    """

    if instruction_arg_mode not in ("chunk", "full"):
        raise ValueError("instruction_arg_mode must be 'chunk' or 'full'")
    instruction_arg = (
        "instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?"
        if instruction_arg_mode == "chunk"
        else "instruction_data"
    )

    rendered = MATCH_ARM_TEMPLATE.format(
        discriminator=func_cfg.discriminator,
        title=to_title(func_cfg.name),
        function_name=func_cfg.name,
        account_line=account_expr,
        account_line_comment=comment_block,
        instruction_arg=instruction_arg,
    )

    return rendered


# Parsing helpers (supporting) ------------------------------------------------
# REVIEW SKIP: The helpers below identify function boundaries; they support the
# pipeline but rarely require changes.

def find_matching_brace(text: str, start: int) -> int:
    depth = 0
    i = start
    length = len(text)
    while i < length:
        ch = text[i]
        # Skip braces that appear inside comments.
        if text.startswith("//", i):
            newline = text.find("\n", i)
            if newline == -1:
                return length - 1
            i = newline + 1
            continue
        if text.startswith("/*", i):
            close = text.find("*/", i + 2)
            if close == -1:
                raise ValueError("Unterminated block comment")
            i = close + 2
            continue
        # Treat string and char literals as opaque so we ignore delimiters inside them.
        if ch == '"':
            i += 1
            while i < length:
                if text[i] == "\\":
                    i += 2
                elif text[i] == '"':
                    i += 1
                    break
                else:
                    i += 1
            continue
        if ch == "'":
            i += 1
            while i < length:
                if text[i] == "\\":
                    i += 2
                elif text[i] == "'":
                    i += 1
                    break
                else:
                    i += 1
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError(f"Unmatched braces starting at index {start}")


def extract_test_functions(text: str) -> Dict[str, str]:
    pattern = re.compile(r"(?m)^[ \t]*(?:pub[ \t]+)?fn[ \t]+(?P<name>test_process_[A-Za-z0-9_]+)\s*\(")
    functions: Dict[str, str] = {}
    for match in pattern.finditer(text):
        name = match.group("name")
        fn_start = match.start()
        # Capture any leading doc comments or attributes that belong to the harness.
        start = fn_start
        while start > 0:
            prev_newline = text.rfind("\n", 0, start - 1)
            if prev_newline == -1:
                start = 0
                break
            line_start = prev_newline + 1
            line = text[line_start:start]
            stripped = line.strip()
            if stripped.startswith("///") or stripped.startswith("#["):
                start = line_start
                continue
            if stripped == "":
                start = line_start
                continue
            break
        brace_start = text.find("{", match.end())
        if brace_start == -1:
            raise ValueError(f"Missing body for {name}")
        brace_end = find_matching_brace(text, brace_start)
        snippet = text[start : brace_end + 1]
        functions[name] = snippet.strip("\n")
    return functions


# Support scaffolding (REVIEW SKIP) -------------------------------------------
@dataclass
class SectionRule:
    separator: str
    trailing_newline: bool


@dataclass
class Replacement:
    raw_from: str
    replacement: str
    is_regex: bool = False
    pattern: re.Pattern[str] | None = None
    literal_from: str | None = None

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Replacement":
        raw = data["from"]
        replacement = data["to"]
        if raw.startswith("regex:"):
            pattern_text = raw[len("regex:") :]
            pattern = re.compile(pattern_text)
            return cls(
                raw_from=raw,
                replacement=replacement,
                is_regex=True,
                pattern=pattern,
            )
        return cls(
            raw_from=raw,
            replacement=replacement,
            literal_from=raw,
        )

    def clone(self) -> "Replacement":
        if self.is_regex and self.pattern is not None:
            return Replacement(
                raw_from=self.raw_from,
                replacement=self.replacement,
                is_regex=True,
                pattern=re.compile(self.pattern.pattern),
            )
        return Replacement(
            raw_from=self.raw_from,
            replacement=self.replacement,
            literal_from=self.literal_from,
        )


@dataclass
class HarnessConfig:
    comment_out: List[str] = field(default_factory=list)
    replacements: List[Replacement] = field(default_factory=list)
    presets: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> "HarnessConfig":
        return cls(
            comment_out=list(data.get("comment_out", [])),
            replacements=[Replacement.from_dict(item) for item in data.get("replacements", [])],
            presets=list(data.get("presets", [])),
        )

    @staticmethod
    def empty() -> "HarnessConfig":
        return HarnessConfig(
            comment_out=[],
            replacements=[],
            presets=[],
        )

    def clone(self) -> "HarnessConfig":
        return HarnessConfig(
            comment_out=list(self.comment_out),
            replacements=[repl.clone() for repl in self.replacements],
            presets=list(self.presets),
        )

    def expand_presets(
        self,
        preset_map: Dict[str, "HarnessConfig"],
        *,
        cache: Dict[str, "HarnessConfig"] | None = None,
        stack: tuple[str, ...] = (),
    ) -> "HarnessConfig":
        if cache is None:
            cache = {}

        combined = HarnessConfig.empty()
        for preset_name in self.presets:
            if preset_name in cache:
                preset_resolved = cache[preset_name]
            else:
                if preset_name in stack:
                    cycle = " -> ".join(stack + (preset_name,))
                    raise ValueError(f"Circular preset dependency detected: {cycle}")
                if preset_name not in preset_map:
                    raise KeyError(f"Unknown preset `{preset_name}` referenced in harness config")
                preset_resolved = preset_map[preset_name].expand_presets(
                    preset_map,
                    cache=cache,
                    stack=stack + (preset_name,),
                )
                cache[preset_name] = preset_resolved
            combined = merge_harness_configs(combined, preset_resolved)

        own = self.clone()
        own.presets = []
        combined = merge_harness_configs(combined, own)
        combined.comment_out = dedupe_preserve_order(combined.comment_out)
        combined.replacements = dedupe_preserve_order(
            combined.replacements,
            key=lambda repl: (repl.raw_from, repl.replacement, repl.is_regex),
        )
        if stack:
            cache[stack[-1]] = combined
        return combined


def dedupe_preserve_order(
    items: Iterable,
    *,
    key=lambda x: x,
) -> List:
    """Return items without duplicates while honoring the caller-provided key."""
    seen: set = set()
    output: List = []
    for item in items:
        marker = key(item)
        if marker in seen:
            continue
        seen.add(marker)
        output.append(item)
    return output


def merge_harness_configs(base: HarnessConfig, extra: HarnessConfig) -> HarnessConfig:
    return HarnessConfig(
        comment_out=base.comment_out + extra.comment_out,
        replacements=base.replacements + extra.replacements,
        presets=[],
    )


def apply_harness_override(harness: HarnessConfig, override: Dict) -> None:
    if not override:
        return
    if override.get("presets"):
        raise ValueError("Harness overrides cannot add presets; presets are expanded during config load.")
    if "comment_out" in override:
        harness.comment_out.extend(override["comment_out"])
    if "replacements" in override:
        harness.replacements.extend(Replacement.from_dict(item) for item in override["replacements"])
    harness.comment_out = dedupe_preserve_order(harness.comment_out)
    harness.replacements = dedupe_preserve_order(
        harness.replacements,
        key=lambda repl: (repl.raw_from, repl.replacement, repl.is_regex),
    )


def apply_function_override(func_cfg: FunctionConfig, override: Dict) -> None:
    harness_override = override.get("harness")
    if harness_override:
        apply_harness_override(func_cfg.harness, harness_override)


@dataclass
class FunctionConfig:
    name: str
    discriminator: int
    harness: HarnessConfig

    @classmethod
    def from_dict(cls, name: str, data: Dict) -> "FunctionConfig":
        harness = HarnessConfig.from_dict(data["harness"])
        return cls(
            name=name,
            discriminator=data["discriminator"],
            harness=harness,
        )

    def clone(self) -> "FunctionConfig":
        return FunctionConfig(
            name=self.name,
            discriminator=self.discriminator,
            harness=self.harness.clone(),
        )


@dataclass
class OutputConfig:
    name: str
    template: Path
    target: Path
    placeholders: Dict[str, str]
    section_rules: Dict[str, SectionRule]
    functions: List[FunctionConfig]
    overrides: Dict[str, Dict]


@dataclass
class SyncConfig:
    source: Path
    presets: Dict[str, HarnessConfig]
    outputs: List[OutputConfig]

    @classmethod
    def load(cls, path: Path) -> "SyncConfig":
        data = json.loads(path.read_text())
        preset_map = {
            name: HarnessConfig.from_dict(item)
            for name, item in data.get("presets", {}).items()
        }
        preset_cache: Dict[str, HarnessConfig] = {}
        for preset_name in preset_map:
            if preset_name not in preset_cache:
                preset_cache[preset_name] = preset_map[preset_name].expand_presets(
                    preset_map,
                    cache=preset_cache,
                    stack=(preset_name,),
                )

        function_defs: Dict[str, FunctionConfig] = {}
        for name, item in data.get("functions", {}).items():
            func = FunctionConfig.from_dict(name, item)
            function_defs[name] = FunctionConfig(
                name=func.name,
                discriminator=func.discriminator,
                harness=func.harness.expand_presets(preset_map, cache=preset_cache),
            )

        outputs: List[OutputConfig] = []
        for output_entry in data.get("outputs", []):
            section_rules = {
                name: SectionRule(**rule) for name, rule in output_entry["sections"].items()
            }
            function_names = output_entry.get("functions", [])
            overrides = output_entry.get("function_overrides", {})
            if not function_names:
                resolved_functions = list(function_defs.values())
            else:
                resolved_functions = []
                for func_name in function_names:
                    if func_name not in function_defs:
                        raise KeyError(f"Unknown function `{func_name}` referenced in output `{output_entry.get('name', '<unnamed>')}`")
                    resolved_functions.append(function_defs[func_name])

            cloned_functions: List[FunctionConfig] = []
            for func in resolved_functions:
                clone = func.clone()
                override_spec = overrides.get(clone.name)
                if override_spec:
                    apply_function_override(clone, override_spec)
                cloned_functions.append(clone)

            outputs.append(
                OutputConfig(
                    name=output_entry["name"],
                    template=REPO_ROOT / output_entry["template"],
                    target=REPO_ROOT / output_entry["target"],
                    placeholders=output_entry["placeholders"],
                    section_rules=section_rules,
                    functions=cloned_functions,
                    overrides=overrides,
                )
            )

        return cls(
            source=REPO_ROOT / data["source"],
            presets=preset_cache,
            outputs=outputs,
        )


def replace_placeholder(text: str, placeholder: str, replacement: str) -> str:
    if placeholder not in text:
        raise RuntimeError(f"Placeholder `{placeholder}` not found in template")
    return text.replace(placeholder, replacement if replacement else placeholder, 1)


if __name__ == "__main__":
    main()
