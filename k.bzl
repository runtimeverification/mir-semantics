load("@bazel_skylib//lib:collections.bzl", "collections")

KompileInfo = provider(fields=["files"])
KtrustedInfo = provider(fields=["trusted"])
KproveInfo = provider(fields=["spec", "definition", "command"])

def _extract_includes(ctx):
  all_files = ctx.files.srcs
  for dep in ctx.attr.deps:
    all_files = all_files + dep[DefaultInfo].files.to_list()

  paths = collections.uniq([s.root.path for s in all_files])
  joined_paths = ':'.join([p for p in paths if p])
  if not joined_paths:
    return ':'
  return joined_paths

def _kompile_impl(ctx):
  output_files = [
    ctx.actions.declare_file(ctx.label.name + '-kompiled/' + name)
    for name in [
      'allRules.txt', 'backend.txt', 'cache.bin', 'compiled.bin',
      'compiled.txt', 'configVars.sh', 'definition.kore',
      'haskellDefinition.bin',
      'macros.kore', 'mainModule.txt',
      'mainSyntaxModule.txt', 'parsed.txt', 'scanner',
      'syntaxDefinition.kore', 'timestamp']
  ]
  if len(ctx.files.srcs) != 1:
    fail
  input_names = [_extract_includes(ctx), output_files[0].path] + [s.path for s in ctx.files.srcs]
  # TODO: Make this work if the file name is not based on the target name.
  ctx.actions.run(
      inputs=depset(ctx.files.srcs, transitive = [dep[DefaultInfo].files for dep in ctx.attr.deps]),
      outputs=output_files,
      arguments=input_names,
      progress_message="Kompiling %s" % ctx.files.srcs[0].path,
      executable=ctx.executable.kompile_tool)

  return [
      DefaultInfo(
          files = depset(
              output_files,
              transitive = [dep[DefaultInfo].files for dep in ctx.attr.deps]
          ),
      ),
      KompileInfo(files=output_files),
  ]

kompile = rule(
    implementation = _kompile_impl,
    attrs = {
        "deps": attr.label_list(),
        "srcs": attr.label_list(allow_files = [".k"]),
        "kompile_tool": attr.label(
            executable = True,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:kompile_tool"),
        ),
    },
    executable = False,
)

def _klibrary_impl(ctx):
  if len(ctx.files.srcs) != 1:
    fail
  input_names = [s.path for s in ctx.files.srcs]
  output_dir = ctx.actions.declare_directory(ctx.label.name + '-kompiled')
  # TODO: Make this work if the file name is not based on the target name.
  ctx.actions.run(
      inputs=depset(ctx.files.srcs, transitive = [dep[DefaultInfo].files for dep in ctx.attr.deps]),
      outputs=[output_dir],
      arguments= [_extract_includes(ctx)] + input_names,
      progress_message="Checking %s" % ctx.files.srcs[0].path,
      executable=ctx.executable.kompile_tool)
  return [
      DefaultInfo(
          files = depset(ctx.files.srcs + [ output_dir ], transitive = [dep[DefaultInfo].files for dep in ctx.attr.deps]),
      )
  ]

klibrary = rule(
    implementation = _klibrary_impl,
    attrs = {
        "deps": attr.label_list(),
        "srcs": attr.label_list(allow_files = [".k"]),
        "kompile_tool": attr.label(
            executable = True,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:kompile_e_tool"),
        ),
    },
)

def _ktrusted_impl(ctx):
  if len(ctx.files.srcs) != 1:
    fail

  tmp_file = ctx.actions.declare_file(ctx.label.name + ".tmp.k")
  ctx.actions.run(
      inputs=depset(ctx.files.srcs),
      outputs=[tmp_file],
      arguments=['trusted', ctx.files.srcs[0].path, tmp_file.path],
      progress_message="Trusting %s" % ctx.files.srcs[0].path,
      executable=ctx.executable.ktrusted_tool)

  output_file = ctx.actions.declare_file(ctx.label.name + ".k")
  all_trusted = []
  for dep in ctx.attr.trusted:
    all_trusted += dep[KtrustedInfo].trusted
  ctx.actions.run(
      inputs=depset([tmp_file] + all_trusted),
      outputs=[output_file],
      arguments=[output_file.path, tmp_file.path] + [s.path for s in all_trusted],
      progress_message="Merging %s" % ctx.files.srcs[0].path,
      executable=ctx.executable.kmerge_tool)
  return [
      DefaultInfo(
          files = depset([output_file]),
      ),
      KtrustedInfo(
          trusted = output_file,
      )
  ]

ktrusted = rule(
    implementation = _ktrusted_impl,
    attrs = {
        "srcs": attr.label_list(allow_files = [".k"]),
        "trusted": attr.label_list(providers=[DefaultInfo, KtrustedInfo]),
        "ktrusted_tool": attr.label(
            executable = True,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:ktrusted_tool"),
        ),
        "kmerge_tool": attr.label(
            executable = True,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:kmerge_tool"),
        ),
    },
)

def _merge_trusted(input_file, trusted_attr, kmerge, actions, merged_file):
  all_trusted = []
  for dep in trusted_attr:
    all_trusted += [dep[KtrustedInfo].trusted]
  actions.run(
      inputs=depset([input_file] + all_trusted),
      outputs=[merged_file],
      arguments=[merged_file.path, input_file.path] + [s.path for s in all_trusted],
      progress_message="Preparing %s" % input_file.path,
      executable=kmerge)

def _kprove_kompile_impl(ctx):
  if len(ctx.files.srcs) != 1:
    fail

  tmp_file = ctx.actions.declare_file(ctx.label.name + ".tmp-proof.k")
  ctx.actions.run(
      inputs=depset([ctx.files.srcs[0]]),
      outputs=[tmp_file],
      arguments=['proof', ctx.files.srcs[0].path, tmp_file.path],
      progress_message="Preparing %s" % ctx.files.srcs[0].path,
      executable=ctx.executable.ktrusted_tool)

  merged_file = ctx.actions.declare_file(ctx.label.name + '.k')

  _merge_trusted(
      tmp_file,
      ctx.attr.trusted,
      ctx.executable.kmerge_tool,
      ctx.actions,
      merged_file)

  output_spec = ctx.actions.declare_file(ctx.label.name + '.spec.kore')
  output_definition = ctx.actions.declare_file(ctx.label.name + '.definition.kore')
  output_command = ctx.actions.declare_file(ctx.label.name + '.command')

  output_kompile_files = [
    ctx.actions.declare_file(ctx.label.name + '-kompiled/' + name)
    for name in [
      'allRules.txt', 'cache.bin', 'compiled.bin', 'compiled.txt',
      # 'compiled.json',
      'configVars.sh', 'definition.kore', 'macros.kore',
      'mainModule.txt', 'parsed.txt', 'syntaxDefinition.kore', 'timestamp']
  ]

  runfiles = depset(
      [merged_file, ctx.executable.kprove_kompile_tool]
      + ctx.attr.semantics[KompileInfo].files
      + ctx.attr.k_distribution[DefaultInfo].files.to_list()
  )
  ctx.actions.run(
      inputs=runfiles.to_list(),
      outputs=[output_spec, output_definition, output_command] + output_kompile_files,
      arguments=[
          ctx.attr.semantics[KompileInfo].files[0].path,
          ctx.files.srcs[0].path,
          merged_file.path,
          output_spec.path,
          output_definition.path,
          output_command.path,
          output_kompile_files[0].path
      ],
      progress_message="Generating kore for %s" % ctx.files.srcs[0].path,
      executable=ctx.executable.kprove_kompile_tool)
  return [
      KompileInfo(files=output_kompile_files),
      KproveInfo(
          spec = output_spec,
          definition = output_definition,
          command = output_command
      )
  ]

kprove_kompile = rule(
    implementation = _kprove_kompile_impl,
    attrs = {
        "srcs": attr.label_list(allow_files = [".k"]),
        "trusted": attr.label_list(providers=[DefaultInfo, KtrustedInfo]),
        "semantics": attr.label(mandatory=True, providers=[DefaultInfo, KompileInfo]),
        "kprove_kompile_tool": attr.label(
            executable = True,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:kprove_kompile_tool"),
        ),
        "ktrusted_tool": attr.label(
            executable = True,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:ktrusted_tool"),
        ),
        "kmerge_tool": attr.label(
            executable = True,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:kmerge_tool"),
        ),
        "k_distribution": attr.label(
            executable = False,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:k_release"),
        ),
    },
)

def _kore_test_impl(ctx):

  script_file = ctx.actions.declare_file(ctx.label.name + '-runner.sh')

  tool_call = "kompile-tool/kore_tool %s %s %s %s %s %s %s" % (
      ctx.attr.module,
      ctx.attr.kompiled[KompileInfo].files[0].short_path,
      ctx.attr.kompiled[KproveInfo].definition.short_path,
      ctx.attr.kompiled[KproveInfo].spec.short_path,
      ctx.attr.kompiled[KproveInfo].command.short_path,
      ctx.label.name + '.output.k',
      ctx.attr.breadth)

  command_parts = [
      "pushd $(pwd) > /dev/null",
      "%s --debug" % tool_call,
      "popd > /dev/null",
  ]
  script_lines = [
      "#!/usr/bin/env bash",
      "",
      "echo 'To debug:'",
      'echo "%s"' % ("; ".join(command_parts)),
      "%s %s || (echo 'Proof FAILED!'; false)" % (tool_call, '"$@"'),
  ]
  ctx.actions.write(script_file, "\n".join(script_lines), is_executable = True)
  runfiles = ctx.runfiles(
      [
          ctx.attr.kompiled[KproveInfo].definition,
          ctx.attr.kompiled[KproveInfo].spec,
          ctx.attr.kompiled[KproveInfo].command,
          ctx.executable.kore_tool,
      ]
      + ctx.attr.kompiled[KompileInfo].files
      + ctx.attr.k_distribution[DefaultInfo].files.to_list()
      + ctx.attr.debug_script[DefaultInfo].files.to_list()
  )
  return [
      DefaultInfo(
          runfiles = runfiles,
          executable = script_file,
      )
  ]

kore_test = rule(
    implementation = _kore_test_impl,
    attrs = {
        "kompiled": attr.label(providers=[KproveInfo], mandatory=True),
        "module": attr.string(mandatory=True),
        "breadth": attr.string(mandatory=True),
        "kore_tool": attr.label(
            executable = True,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:kore_tool"),
        ),
        "k_distribution": attr.label(
            executable = False,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:k_release"),
        ),
        "debug_script": attr.label(
            executable = False,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:kast_script"),
        ),
    },
    test = True,
)


def _kast_test_impl(ctx):

  script_file = ctx.actions.declare_file(ctx.label.name + '-runner.sh')

  tool_call = "kompile-tool/kast '%s' '%s' '%s' '%s'" % (
      ctx.attr.semantics[KompileInfo].files[0].short_path,
      ctx.files.src[0].short_path,
      ctx.attr.sort,
      ctx.label.name + '.output.kore')

  command_parts = [
      "pushd $(pwd) > /dev/null",
      tool_call,
      "popd > /dev/null",
  ]
  script_lines = [
      "#!/usr/bin/env bash",
      "",
      "echo PATH=$PATH",
      "echo 'To debug:'",
      'echo "%s"' % ("; ".join(command_parts)),
      "%s || (echo 'Syntax FAILED!'; false)" % (tool_call),
  ]
  ctx.actions.write(script_file, "\n".join(script_lines), is_executable = True)
  runfiles = ctx.runfiles(
      [ctx.files.src[0]]
      + ctx.attr._kast_tool[DefaultInfo].files.to_list()
      + ctx.attr._kast_tool[DefaultInfo].default_runfiles.files.to_list()
      + ctx.attr.semantics[KompileInfo].files
  )
  return [
      DefaultInfo(
          runfiles = runfiles,
          executable = script_file,
      )
  ]

kast_test = rule(
    implementation = _kast_test_impl,
    attrs = {
        "src": attr.label(mandatory=True, allow_single_file = [".mir"]),
        "semantics": attr.label(providers=[KompileInfo], mandatory=True),
        "sort": attr.string(mandatory=True),
        "_kast_tool": attr.label(
            executable = True,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:kast"),
        ),
    },
    test = True,
)

def _kprovex_test_impl(ctx):
  if len(ctx.files.srcs) != 1:
    fail

  tmp_file = ctx.actions.declare_file(ctx.label.name + ".tmp-proof.k")
  ctx.actions.run(
      inputs=depset([ctx.files.srcs[0]]),
      outputs=[tmp_file],
      arguments=['proof', ctx.files.srcs[0].path, tmp_file.path],
      progress_message="Preparing %s" % ctx.files.srcs[0].path,
      executable=ctx.executable.ktrusted_tool)

  merged_file = ctx.actions.declare_file(ctx.label.name + '-merged.k')

  _merge_trusted(
      tmp_file,
      ctx.attr.trusted,
      ctx.executable.kmerge_tool,
      ctx.actions,
      merged_file)

  script_file = ctx.actions.declare_file(ctx.label.name + '-runner.sh')
  tool_call = "kompile-tool/kprovex_tool %s %s %s" % (
          ctx.attr.semantics[KompileInfo].files[0].short_path,
          ctx.files.srcs[0].short_path,
          merged_file.short_path)
  command_parts = [
      "pushd $(pwd) > /dev/null",
      "%s --debug" % tool_call,
      "popd > /dev/null",
  ]
  script_lines = [
      "#!/usr/bin/env bash",
      "",
      "echo 'To debug:'",
      'echo "%s"' % ("; ".join(command_parts)),
      "%s %s || (echo 'Proof FAILED!'; false)" % (tool_call, '"$@"'),
  ]
  ctx.actions.write(script_file, "\n".join(script_lines), is_executable = True)

  runfiles = ctx.runfiles(
      [ merged_file
      , ctx.executable.kprovex_tool
      ]
      + ctx.attr.semantics[KompileInfo].files
      + ctx.attr.k_distribution[DefaultInfo].files.to_list()
      + ctx.attr.debug_script[DefaultInfo].files.to_list()
  )
  return [
      DefaultInfo(
          runfiles = runfiles,
          executable = script_file,
      )
  ]

kprovex_test = rule(
    implementation = _kprovex_test_impl,
    attrs = {
        "srcs": attr.label_list(allow_files = [".k"]),
        "trusted": attr.label_list(providers=[DefaultInfo, KtrustedInfo]),
        "semantics": attr.label(mandatory=True, providers=[DefaultInfo, KompileInfo]),
        "kprovex_tool": attr.label(
            executable = True,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:kprovex_tool"),
        ),
        "ktrusted_tool": attr.label(
            executable = True,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:ktrusted_tool"),
        ),
        "kmerge_tool": attr.label(
            executable = True,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:kmerge_tool"),
        ),
        "k_distribution": attr.label(
            executable = False,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:k_release"),
        ),
        "debug_script": attr.label(
            executable = False,
            cfg = "exec",
            allow_files = True,
            default = Label("//kompile-tool:kast_script"),
        ),
        "breadth": attr.string(mandatory=True),
    },
    test = True,
)

def kprove_test(*, name, srcs, trusted=[], semantics, breadth="1", timeout="short"):
  kprove_kompile(
    name = "%s-kompile" % name,
    srcs = srcs,
    trusted = trusted,
    semantics = semantics,
  )

  kore_test(
    name = name,
    module = name.upper(),
    breadth = breadth,
    kompiled = ":%s-kompile" % name,
    timeout = timeout,
  )
