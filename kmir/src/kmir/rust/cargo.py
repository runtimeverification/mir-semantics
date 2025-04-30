from __future__ import annotations

import json
import logging
import subprocess
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.utils import run_process_2

if TYPE_CHECKING:
    from typing import Any, Final

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'

SMIR_JSON_DIR: Final = Path(__file__).parents[4] / 'deps/stable-mir-json/'


class CargoProject:
    working_directory: Path

    def __init__(self, working_directory: Path) -> None:
        self.working_directory = working_directory

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


def cargo_get_smir_json(rs_file: Path) -> dict[str, Any]:
    smir_json_result = SMIR_JSON_DIR / rs_file.with_suffix('.smir.json').name
    run_process_2(['cargo', 'run', '--', '-Zno-codegen', str(rs_file)], cwd=SMIR_JSON_DIR)
    json_smir = json.loads(smir_json_result.read_text())
    _LOGGER.info(f'Loaded: {smir_json_result}')
    smir_json_result.unlink()
    _LOGGER.info(f'Deleted: {smir_json_result}')
    return json_smir
