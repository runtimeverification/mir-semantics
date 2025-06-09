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

if TYPE_CHECKING:
    from typing import Any, Final

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'

IN_TREE_SMIR_JSON_DIR: Final = Path(__file__).parents[3] / 'deps/.stable-mir-json/'


class CargoProject:
    working_directory: Path

    def __init__(self, working_directory: Path) -> None:
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

    def smir_for(self, target: str) -> Path:
        """Gets the latest smir json in the target directory for the given target. Raises a RuntimeError if none exist."""

        is_artifact = lambda message: message.get('reason') == 'compiler-artifact'
        is_my_target = lambda artifact: artifact.get('target', {}).get('name') == target
        artifact = next(message for message in self.build_messages if is_artifact(message) and is_my_target(message))
        executable_name = Path(artifact['executable'])
        deps_dir = executable_name.parent / 'deps'

        # Get the smir file(s) and sort them by modified time
        smir_files = deps_dir.glob(f'{target}*.smir.json')
        sorted_smir_files = sorted(smir_files, key=lambda f: f.stat().st_mtime, reverse=True)

        if len(sorted_smir_files) == 0:
            raise RuntimeError(
                f'Unable to find smir json for target {target!r}. Have you built it using stable-mir-json?'
            )

        # Return the most recently modified smir file
        return sorted_smir_files[0]

    def smir_files_for_project(self, clean: bool = False) -> list[Path]:
        # run a cargo build command with stable-mir-json as the rustc compiler
        # to be 100% safe, run cargo clean if there are no *smir.json files
        # assumes cargo and stable-mir-json are on the path (with these names)

        if clean:
            _LOGGER.info(f'Running "cargo clean" in {self.working_directory}')
            command_result = subprocess.run(
                ['cargo', 'clean'], capture_output=True, text=True, cwd=self.working_directory
            )
            for l in command_result.stderr.splitlines():
                _LOGGER.info(l)

        _LOGGER.info(f'Running "cargo build" with stable-mir-json in {self.working_directory}')
        env = {**os.environ, 'RUSTC': str(self.stable_mir_json)}
        cmd = ['cargo', 'build', '--message-format=json']
        command_result = subprocess.run(cmd, env=env, capture_output=True, text=True, cwd=self.working_directory)

        for l in command_result.stderr.splitlines():
            _LOGGER.info(l)
        _LOGGER.debug(command_result.stdout)

        messages = [json.loads(line) for line in command_result.stdout.splitlines()]

        artifacts = [
            (Path(message['filenames'][0]), message.get('executable') is not None)
            for message in messages
            if message.get('reason') == 'compiler-artifact'
        ]

        libraries = []
        executables = []
        for file, is_exec in artifacts:
            _LOGGER.debug(f'{"Artifact" if is_exec else "Library"} at ../{file.parent.name}/{file.name}')
            if is_exec:
                smirs = list((file.parent / 'deps').glob(f'{file.name}*.smir.json'))
                executables.append(smirs[0])
            else:
                name = file.stem.removeprefix('lib') + '.smir.json'
                libraries.append(file.parent / name)

        _LOGGER.debug(f'Result: {executables + libraries}')

        return executables + libraries

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
    # otherwise try to find `stable-mir-json` on the path (in a docker container)
    stable_mir_on_path = shutil.which('stable-mir-json')
    on_path = [Path(stable_mir_on_path)] if stable_mir_on_path is not None else []
    # otherwise try to use `$HOME/.stable-mir-json/{release,debug}.sh`
    in_home = [
        Path.home() / '.stable-mir-json' / 'release.sh',
        Path.home() / '.stable-mir-json' / 'debug.sh',
    ]

    candidates = in_tree + on_path + in_home

    existing = [cand for cand in candidates if cand.exists()]

    if len(existing) < 1:
        _LOGGER.error('Cannot build: Unable to find stable-mir-json executable. Tried')
        for p in candidates:
            _LOGGER.error(f'Path {p}')
        _LOGGER.error('Please install into $HOME or ensure you have an executable `stable-mir-json` on the path.')
        raise FileNotFoundError('stable-mir-json not installed.')
    else:
        _LOGGER.debug(f'Using stable-mir-json from {existing[0]}')
        return existing[0]
