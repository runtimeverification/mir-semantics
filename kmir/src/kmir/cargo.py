from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.utils import run_process_2

from .linker import link
from .smir import SMIRInfo

if TYPE_CHECKING:
    from typing import Any, Final

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'

IN_TREE_SMIR_JSON_DIR: Final = Path(__file__).parents[3] / 'deps/.stable-mir-json/'


class CargoProject:
    working_directory: Path

    def __init__(self, working_directory: Path) -> None:
        # rudimentary check that this is in fact a cargo project directory
        if not (working_directory / 'Cargo.toml').exists():
            raise FileNotFoundError(f'{working_directory}: Not a cargo project.')
        self.working_directory = working_directory

    @cached_property
    def stable_mir_json(self) -> Path:
        return stable_mir_json()

    @cached_property
    def metadata(self) -> dict:
        """Metadata about the cargo project"""

        command = ['cargo', 'metadata', '--format-version', '1']
        command_result = subprocess.run(command, capture_output=True, text=True, cwd=self.working_directory)
        metadata = json.loads(command_result.stdout)
        return metadata

    @cached_property
    def manifest(self) -> dict:
        """Information about the Cargo.toml file"""

        command = ['cargo', 'read-manifest']
        command_result = subprocess.run(command, capture_output=True, text=True, cwd=self.working_directory)
        manifest = json.loads(command_result.stdout)
        return manifest

    @property
    def build_messages(self) -> list[dict]:
        """Output of messages from `cargo build`"""

        command = ['cargo', 'build', '--message-format=json']
        command_result = subprocess.run(command, capture_output=True, text=True, cwd=self.working_directory)
        split_command_result = command_result.stdout.splitlines()
        messages = [json.loads(message) for message in split_command_result]
        return messages

    def smir_for_project(self, clean: bool = False) -> SMIRInfo:
        # run a cargo build command with stable_mir_json as the rustc compiler
        # and run cargo clean before (optional)
        # assumes cargo and stable_mir_json are on the path (with these names)

        # TODO check if linked file present (not present => rebuild unconditionally)

        if clean:
            _LOGGER.info(f'Running "cargo clean" in {self.working_directory}')
            command_result = subprocess.run(
                ['cargo', 'clean'], capture_output=True, text=True, cwd=self.working_directory
            )
            for l in command_result.stderr.splitlines():
                _LOGGER.info(l)

        _LOGGER.info(f'Running "cargo build" with stable_mir_json in {self.working_directory}')
        env = {**os.environ, 'RUSTC': str(self.stable_mir_json)}
        cmd = ['cargo', 'build', '--message-format=json']
        command_result = subprocess.run(cmd, env=env, capture_output=True, text=True, cwd=self.working_directory)

        for l in command_result.stderr.splitlines():
            _LOGGER.info(l)
        _LOGGER.debug(command_result.stdout)

        messages = [json.loads(line) for line in command_result.stdout.splitlines()]

        if command_result.returncode != 0:
            _LOGGER.error('Cargo compilation failed!')
            for msg in [m['message'] for m in messages if m.get('reason') == 'compiler-message']:
                _LOGGER.error(msg['level'] + '\n' + msg['rendered'])
            raise Exception('Cargo compilation failed')

        artifacts = [
            (Path(message['filenames'][0]), message['target']['kind'][0])
            for message in messages
            if message.get('reason') == 'compiler-artifact'
        ]

        targets = []
        exe = None
        for file, kind in artifacts:
            _LOGGER.debug(f'Artifact ({kind}) at ../{file.parent.name}/{file.name}')
            if kind == 'bin':
                # we can only support a single executable at the moment
                if exe is not None:
                    raise FileExistsError(
                        f'Already linking executable {exe} but found {file.name}.'
                        'Several execuatbles not supported at the moment.'
                    )
                exe = file.name
                glob = exe.replace('-', '_') + '-*.smir.json'
                # executables are in the target directory with the crate name and have a hex ID suffix in `deps`
                location = file.parent / 'deps'
            else:
                # lib, rlib, dylib, cdylib may be in `deps` or in target and have prefix 'lib'
                in_deps = file.parent.name == 'deps'
                location = file.parent if in_deps else file.parent / 'deps'
                # files for lib and rlib require a hex ID suffix unless in `deps`, *.dylib (or *.so) ones don't
                is_rlib = file.suffix == '.rlib'
                glob = file.stem.removeprefix('lib') + ('' if in_deps or not is_rlib else '-*') + '.smir.json'

            related_files = list(location.glob(glob))
            if not related_files:
                _LOGGER.error('SMIR JSON files not found after building, you must run `cargo clean` and rebuild.')
                raise FileNotFoundError(f'{location}/{glob}')
            targets.append(related_files[0])

        _LOGGER.debug(f'Files: {targets}')

        # link all files together and write linked output to target location
        # if any file is not found, cargo clean needs to be run.
        try:
            smirs = [SMIRInfo.from_file(f) for f in targets]
        except FileNotFoundError:
            _LOGGER.error('SMIR JSON files not found after building, you must run `cargo clean` and rebuild.')
            raise
        linked = link(smirs)
        linked_file = targets[-1].parent.parent / 'linked.smir.json'
        linked.dump(linked_file)

        return linked

    @cached_property
    def default_target(self) -> str:
        """Returns the name of the default binary target. If it can't find a default, raises a RuntimeError"""

        default_run = self.manifest.get('default_run')
        if isinstance(default_run, str):
            return default_run

        is_bin = lambda target: any(kind == 'bin' for kind in target.get('kind'))
        targets = self.manifest.get('targets')
        assert isinstance(targets, list)
        bin_targets = [target.get('name') for target in targets if is_bin(target)]

        if len(bin_targets) != 1:
            raise RuntimeError(
                f"Can't determine which binary to run. Use --bin, or the 'default-run' manifest key. Found {bin_targets}"
            )

        return bin_targets[0]


def cargo_get_smir_json(rs_file: Path, save_smir: bool = False) -> dict[str, Any]:
    command = [str(stable_mir_json()), '-Zno-codegen', str(rs_file.resolve())]
    smir_json_result = Path.cwd() / rs_file.with_suffix('.smir.json').name
    run_process_2(command)
    json_smir = json.loads(smir_json_result.read_text())
    _LOGGER.info(f'Loaded: {smir_json_result}')
    if save_smir:
        _LOGGER.info(f'SMIR JSON available at: {smir_json_result}')
    else:
        smir_json_result.unlink()
        _LOGGER.info(f'Deleted: {smir_json_result}')
    return json_smir


def stable_mir_json() -> Path:
    # prefer in-tree executables if they exist
    in_tree = [
        IN_TREE_SMIR_JSON_DIR / 'release.sh',
        IN_TREE_SMIR_JSON_DIR / 'debug.sh',
    ]
    # otherwise try to find `stable_mir_json` on the path (in a docker container)
    stable_mir_on_path = shutil.which('stable_mir_json')
    on_path = [Path(stable_mir_on_path)] if stable_mir_on_path is not None else []
    # otherwise try to use `$HOME/.stable-mir-json/{release,debug}.sh`
    in_home = [
        Path.home() / '.stable-mir-json' / 'release.sh',
        Path.home() / '.stable-mir-json' / 'debug.sh',
    ]

    candidates = in_tree + on_path + in_home

    existing = [cand for cand in candidates if cand.exists()]

    if len(existing) < 1:
        _LOGGER.error('Cannot build: Unable to find stable_mir_json executable. Tried')
        for p in candidates:
            _LOGGER.error(f'Path {p}')
        _LOGGER.error('Please install into $HOME or ensure you have an executable `stable_mir_json` on the path.')
        raise FileNotFoundError('stable_mir_json not installed.')
    else:
        _LOGGER.debug(f'Using stable_mir_json from {existing[0]}')
        return existing[0]
