from __future__ import annotations

import json
from pathlib import Path

from kmir.cargo import cargo_get_smir_json


def test_cargo_get_smir_json_uses_isolated_temp_dirs(monkeypatch, tmp_path: Path) -> None:
    rs_file = tmp_path / 'assert-true.rs'
    rs_file.write_text('fn main() {}')

    run_dirs: list[Path] = []

    def fake_stable_mir_json() -> Path:
        return Path('/fake/stable_mir_json')

    def fake_run_process_2(command: list[str], *, cwd: Path, **_kwargs: object) -> None:
        run_dirs.append(cwd)
        (cwd / 'assert-true.smir.json').write_text(json.dumps({'cwd': str(cwd), 'command': command}))

    monkeypatch.setattr('kmir.cargo.stable_mir_json', fake_stable_mir_json)
    monkeypatch.setattr('kmir.cargo.run_process_2', fake_run_process_2)

    first = cargo_get_smir_json(rs_file, cwd=tmp_path)
    second = cargo_get_smir_json(rs_file, cwd=tmp_path)

    assert first['cwd'] != second['cwd']
    assert len(run_dirs) == 2
    assert all(path.parent == tmp_path for path in run_dirs)
    assert not (tmp_path / 'assert-true.smir.json').exists()


def test_cargo_get_smir_json_preserves_saved_output(monkeypatch, tmp_path: Path) -> None:
    rs_file = tmp_path / 'assert-true.rs'
    rs_file.write_text('fn main() {}')

    def fake_stable_mir_json() -> Path:
        return Path('/fake/stable_mir_json')

    def fake_run_process_2(command: list[str], *, cwd: Path, **_kwargs: object) -> None:
        (cwd / 'assert-true.smir.json').write_text(json.dumps({'command': command}))

    monkeypatch.setattr('kmir.cargo.stable_mir_json', fake_stable_mir_json)
    monkeypatch.setattr('kmir.cargo.run_process_2', fake_run_process_2)

    result = cargo_get_smir_json(rs_file, cwd=tmp_path, save_smir=True)

    assert result['command'][0] == '/fake/stable_mir_json'
    assert (tmp_path / 'assert-true.smir.json').is_file()
