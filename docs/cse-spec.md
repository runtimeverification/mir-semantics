# CSE (Compositional Symbolic Execution) Specification

## 1. Overview

CSE enables modular verification of MIR programs by:
1. **Summarizing** callee functions as rewrite rules (pre-condition → post-condition)
2. **Reusing** those summaries in caller proofs to skip re-executing callee internals

**Prerequisite**: This specification assumes the `slotStore` refactor (PR #1059), where runtime locals are stored in a global `<slotStore>` map keyed by stable slot handles, and `Value::Reference` uses `slotPlace(SLOT, projections)` instead of stack-relative offsets.

A summary is a **K rewrite rule** that matches a function call by name and rewrites it to the function's effect:

```k
rule <k> #execTerminatorCall(_, FUNC, ARGS, DEST, TARGET, _UNWIND, _SPAN)
      => #setLocalValue(DEST, RET_VALUE) ~> #execBlockIdx(TARGET)
     </k>
     <slotStore> ... SLOT_A |-> VAL_A  SLOT_B |-> VAL_B ... </slotStore>
  requires #functionName(FUNC) ==String "package::module::function_name"
   andBool PATH_CONSTRAINTS
  [priority(30)]
```

This is structurally identical to how p-token cheatcodes work (e.g., `cheatcode_is_account`). CSE summaries are **automatically generated cheatcodes**.

## 2. Definitions

- **Callee proof**: A standalone proof of a function `f`, producing summaries
- **Summary rule**: A K rewrite rule encoding one execution path of `f`
- **Reachable slot set**: The set of slotStore entries reachable by following reference chains from `f`'s arguments
- **Terminal value**: A value in slotStore that is not a Reference or PtrLocal (the end of a dereference chain)
- **Caller proof**: A proof that uses summary rules instead of re-executing callee bodies
- **Split**: A deterministic branch with mutually exclusive constraints (from `SwitchInt`)
- **Cover**: A leaf node that is subsumed by the target node

## 3. Why slotStore Enables CSE

### 3.1 The Problem with Stack-Relative References (Pre-PR #1059)

Before slotStore, references encoded stack depth:
```
Reference(offset=2, place(local(3), proj), mut, meta)
```
- `#traverseProjection` needed `STACK[offset-1]` to dereference
- Callee summaries were bound to a specific caller stack depth
- Summaries could not be reused across different callers

### 3.2 Slot-Based References (Post-PR #1059)

After slotStore, references encode a global slot handle:
```
Reference(slotPlace(SLOT_ID, proj), mut, meta)
```
- `#traverseProjection` looks up `<slotStore>[SLOT_ID]` — no stack needed
- `WriteTo` is `toSlot(SLOT_ID)` instead of `toStack(FRAME, LOCAL)`
- `#adjustRef` (stack offset adjustment) is eliminated entirely

### 3.3 Consequence for CSE

Summary rules only need `<k>` and optionally `<slotStore>`:
- No `<stack>` — push/pop is internal to the callee, invisible in the summary
- No `<currentFrame>` — `#setLocalValue` internally resolves the caller's frame
- No `<locals>` — replaced by slotStore

## 4. Summary Rule Format

### 4.1 Function Name Matching

Summary rules match by **function name**, not by `Ty` (type ID). This follows the cheatcode pattern:

```k
requires #functionName(FUNC) ==String "pinocchio_token_program::entrypoint::get_account"
```

Rationale: `Ty` is a monomorphization-specific key that may differ across compilations. Function names are stable identifiers.

### 4.2 Pure Function (No SlotStore Side Effects)

For functions that only read data through references and return a value:

```k
rule [cse-get_account-path-1]:
    <k> #execTerminatorCall(_, FUNC, ARGS, DEST, TARGET, _UNWIND, _SPAN)
      => #setLocalValue(DEST, RET_VALUE_1) ~> #execBlockIdx(TARGET)
    </k>
    <slotStore>
      ...
      SLOT_A |-> typedValue(ACCT_INFO_VAL, TY_A, MUT_A)
      SLOT_B |-> typedValue(PAccountAccount(PACC, IAcc(MINT, OWNER, AMOUNT, DELEGATE, STATE, ...)), TY_B, MUT_B)
      ...
    </slotStore>
  requires #functionName(FUNC) ==String "pinocchio_token_program::entrypoint::get_account"
   andBool STATE ==K accountStateInitialized
  [priority(30)]
```

The `<slotStore>` appears without `=>` — it is read-only. The `...` on both sides enables partial map matching.

### 4.3 Function with Side Effects

For functions that modify data through `&mut` references:

```k
rule [cse-set_delegate-path-1]:
    <k> #execTerminatorCall(_, FUNC, ARGS, DEST, TARGET, _UNWIND, _SPAN)
      => #setLocalValue(DEST, RET_VALUE_1) ~> #execBlockIdx(TARGET)
    </k>
    <slotStore>
      ...
      SLOT_B |-> (typedValue(OLD_ACCOUNT, TY_B, MUT_B) => typedValue(NEW_ACCOUNT, TY_B, MUT_B))
      ...
    </slotStore>
  requires #functionName(FUNC) ==String "pinocchio_token_interface::state::account::Account::set_delegate"
   andBool PATH_CONSTRAINTS
  [priority(30)]
```

Only the modified slots have `=>` rewrites. Unmodified slots are matched read-only or omitted entirely.

### 4.4 Reference Chain Resolution for Slot Selection

To determine which slots appear in a summary rule, follow the reference chain from each argument:

```
Argument: operandCopy(place(local(I), proj))
  → evaluates to Reference(slotPlace(SLOT_A, proj_a), ...)
  → SLOT_A |-> typedValue(VAL_A, ...)
    → if VAL_A contains Reference(slotPlace(SLOT_B, ...), ...)
      → SLOT_B |-> typedValue(VAL_B, ...)
        → if VAL_B is NOT a Reference/PtrLocal → STOP (terminal value)
```

**Rule**: Follow references until reaching a non-reference value. All slots visited along the chain are included in the rule's `<slotStore>` pattern. This is the **reachable slot set**.

### 4.5 Variable Scoping

Summary rules must only reference:
- Variables from the caller's argument operands (which resolve to slot handles)
- SlotStore entries in the reachable slot set
- Fresh variables for return values

Callee-internal variables (temporaries, inner locals) must be eliminated. They are not visible in the summary because:
- Callee's `ownedSlots` are created by `setupCalleeData` and cleaned up on return
- Only the callee's effects on pre-existing slots (via `&mut` references) persist

## 5. Callee Proof Requirements

### 5.1 Initial State

The callee proof starts from a **normalized** initial state:
- Symbolic arguments matching the function signature
- Standard callee setup (`setupCalleeData`)
- Target set to `noBasicBlockIdx` (standalone callee)
- Symbolic `<slotStore>` with entries for argument-reachable slots

### 5.2 Proof Completion

A callee proof is **complete** when all leaf nodes are **covers** (subsumed by target) and there are zero stuck nodes.

### 5.3 Extracting Summary Rules from Cover Paths

For each cover node `c` in the callee proof:
1. Trace the path from `init` to `c` through the KCFG
2. Collect all path constraints (from splits along the path)
3. Extract the return value from the final state's `RETVAL_CELL` or `locals[0]`
4. Diff the `<slotStore>` between init and final state to identify modified slots
5. Generate a K rule with:
   - LHS: `#execTerminatorCall(_, FUNC, ...)` + slotStore pattern (reachable slots)
   - RHS: `#setLocalValue(DEST, RET_VALUE) ~> #execBlockIdx(TARGET)` + slotStore updates
   - `requires`: function name match + path constraints

### 5.4 No Cut-Points for Callee Proofs

Cut-point rules (e.g., `termReturnSome`, `termReturnNone`) must NOT be used. They block all returns including inner function returns.

## 6. Interaction with pyk APIs

### 6.1 Summary Rules via `add-module`

Summary rules are compiled K rules injected into the backend:

```python
from pyk.kast.inner import KApply, KVariable, KRewrite, KToken
from pyk.kast.outer import KRule, KFlatModule, KImport

# Build rule for each callee execution path
rules = []
for path in callee_paths:
    rule = KRule(
        body=KRewrite(lhs=..., rhs=...),
        requires=path.constraints,
        ensures=TRUE,
        att=KAtt({'priority': '30', 'label': f'cse-{callee_name}-path-{path.id}'}),
    )
    rules.append(rule)

# Inject as module
module = KFlatModule(f'CSE-SUMMARY-{callee_name}', rules, [KImport('KMIR')])
module_name = cterm_symbolic.add_module(module, name_as_id=True)
```

The backend applies these rules automatically during execution. No `custom_step` needed for summary application.

### 6.2 When `custom_step` IS Needed

`custom_step` is only needed during the **gen phase** to:
- Observe call sites and record argument patterns
- Trigger callee proving on first encounter

During the **reuse phase**, `custom_step` is NOT used for summary application — the compiled rules handle it.

### 6.3 Split vs NDBranch

When multiple summary rules exist for the same function (one per execution path), the backend produces a **Split** because the rules have mutually exclusive `requires` clauses. This is the correct behavior — callee paths are deterministic branches.

`custom_step` must NOT return `NDBranch` for summary application.

## 7. Which Functions to Summarize

### 7.1 Selection Criteria

A function should be summarized if:
1. It has a MIR body (not an intrinsic or extern)
2. It is called by at least one function being verified
3. It is "summary-worthy" (not a trivial std-lib wrapper)
4. Its proof completes within reasonable bounds

### 7.2 Recursive Summarization

Functions are summarized bottom-up:
1. Leaf functions (no further callees) are summarized first
2. Their summaries are used to prove intermediate functions
3. Intermediate functions are then summarized
4. A function like `process_approve` CAN be summarized once its callees are

## 8. Correctness Criteria

### 8.1 Soundness

For each summary rule `pre => post requires C`:
- Execution of `f` from states satisfying `C` must produce states subsumed by `post`
- The union of all path constraints must cover all reachable inputs

### 8.2 Structure Preservation

When a caller proof uses summaries:
- `reuse_splits == baseline_splits`
- `reuse_covers == baseline_covers`
- `reuse_stuck == 0`
- `reuse_ndbranch == 0`

### 8.3 Completeness

A summary is complete if it covers all execution paths of the callee.

## 9. Implementation Phases

### Phase A: Single-Function Summaries as K Rules

1. Rebase CSE on PR #1059 (slotStore)
2. Prove callee functions to completion (all covers)
3. Extract pre/post state pairs, diff slotStore
4. Generate K rewrite rules with function name matching and slot patterns
5. Add rules via `add-module`
6. Prove caller with summary rules active
7. Verify: `reuse_splits == baseline_splits`, `reuse_passed == baseline_passed`

### Phase B: Multi-Level Composition

1. Summarize leaf functions first
2. Use leaf summaries to prove and summarize intermediate functions
3. Summary cache persists across the verification suite

### Phase C: Incremental Re-verification

1. When a callee changes, re-prove only that callee
2. If summary is equivalent, no caller re-verification needed

## 10. Repository Structure and Branches

### 10.1 mir-semantics Repository

| Branch | Purpose | Base |
|--------|---------|------|
| `master` | Upstream baseline | — |
| PR #1059 | slotStore refactor | `master` |
| `feature/cse` | CSE feature | PR #1059 |
| `feature/cse-p-token` | CSE + p-token cheatcodes | `feature/cse` + p-token |

**Branch policy**:
- `feature/cse` must NOT contain p-token-specific rules
- `feature/cse` is rebased on PR #1059
- All CSE logic changes go to `feature/cse` first

### 10.2 solana-token Repository

| Branch | Purpose |
|--------|---------|
| `feature/cse-eval` | CSE evaluation harness |

### 10.3 Branch Sync Flow

```
master ──> PR#1059 (slotStore) ──> feature/cse ──> feature/cse-p-token
                                                       |
                                          (embedded in solana-token/feature/cse-eval)
```

## 11. Validation and Acceptance Testing

### 11.1 Unit-Level Validation (mir-semantics)

**Test**: `test_prove[cse-multi-function]`

Validates:
- CSE proof passes
- Summary generated as K rules (not frontier configs)
- Reuse produces Split (not NDBranch)
- Structure matches baseline

### 11.2 Integration Validation (p-token)

**Hard acceptance criteria** (all must hold):

| # | Criterion | Failure meaning |
|---|-----------|-----------------|
| H1 | CSE reuse PASSES when baseline PASSES | Summary unsound |
| H2 | `reuse_splits == baseline_splits` | Summary loses branches |
| H3 | `reuse_stuck == 0` | Summary incomplete |
| H4 | `reuse_ndbranch == 0` | Using NDBranch instead of Split |
| H5 | Summary rules are K rules via `add-module` | Not compiled rules |
| H6 | Callee proofs have covers, no stuck | Callee proof incomplete |

**Soft optimization targets**:

| # | Target | Goal |
|---|--------|------|
| S1 | Per-test speedup | > 1.0x |
| S2 | Geomean speedup | > 3x |
| S3 | Booster fast path | 100% |

### 11.3 Reproducer Tests

| Reproducer | Tests |
|------------|-------|
| `cse-multi-function.rs` | Basic summary gen + reuse |
| `cse-branching-callee.rs` | Multiple paths → multiple rules → Split |
| `cse-reference-args.rs` | Reference arguments, slotStore pattern matching |
| `cse-side-effects.rs` | `&mut` reference modifications → slotStore diff |

## 12. Paper Artifacts

```bash
cd ~/solana-token-cse-eval/p-token/test-properties
python3 evaluate_cse.py --suite all
```

Generates: `cse_evaluation_results.json`, `cse_paper_table.csv`, `cse_paper_table.tex`

## 13. Non-Goals (Current Scope)

- Loop summarization (loops are unrolled)
- Concurrent/parallel verification
- Summary inference from tests or specifications
- Cross-crate summary sharing (summaries are per-SMIR)
