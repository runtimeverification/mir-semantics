from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from pyk.kore.syntax import And, App, Axiom, EVar, Rewrites, SortApp, Top

from kmir.kompile import _add_exists_quantifiers, _collect_evars, _load_extra_module_rules

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_collect_evars() -> None:
    """Test collecting EVars from nested patterns."""
    var_x = EVar('VarX', SortApp('SortInt'))
    var_y = EVar('VarY', SortApp('SortInt'))
    var_z = EVar('VarZ', SortApp('SortList'))
    pattern = App('test', (), (var_x, App('inner', (), (var_y, var_z, var_x))))

    result = _collect_evars(pattern)

    assert result == {var_x, var_y, var_z}


def test_add_exists_quantifiers() -> None:
    """Test adding exists quantifiers for existential variables."""
    sort = SortApp('SortGeneratedTopCell')
    int_sort = SortApp('SortInt')

    var_x = EVar('VarX', int_sort)
    var_a = EVar('VarA', int_sort)
    var_b = EVar('VarB', int_sort)

    lhs = And(sort, [App('config', (), (var_x,)), Top(sort)])
    rhs = And(sort, [App('result', (), (var_x, var_b, var_a)), Top(sort)])
    pattern = Rewrites(sort, lhs, rhs)
    axiom = Axiom(vars=(), pattern=pattern, attrs=())

    result = _add_exists_quantifiers(axiom)

    # Should have \exists for VarA and VarB (not VarX which is in LHS)
    assert result.text.count(r'\exists') == 2
    assert 'VarA' in result.text
    assert 'VarB' in result.text


def test_load_extra_module_rules_accepts_path_json(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Path inputs for JSON modules should still work for programmatic callers."""
    module_path = tmp_path / 'module.json'
    module_path.write_text('{"node":"KFlatModule","name":"TEST","sentences":[],"imports":[],"att":{}}')

    class DummyModule:
        sentences: list[object] = []

    class DummyKMIR:
        definition = object()

    monkeypatch.setattr('pyk.kast.outer.KFlatModule.from_dict', lambda module_dict: DummyModule())

    assert _load_extra_module_rules(cast('Any', DummyKMIR()), module_path) == []


def test_load_extra_module_rules_uses_requested_haskell_target(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """K source modules should resolve includes from the active haskell target."""
    module_path = tmp_path / 'module.k'
    module_path.write_text('module TEST endmodule')

    class DummyModule:
        name = 'TEST'
        sentences: list[object] = []

    class DummyModuleList:
        modules = [DummyModule()]

    captured: dict[str, object] = {}

    class DummyKMIR:
        definition = object()

        def parse_modules(
            self, file_path: Path, *, module_name: str, include_dirs: tuple[Path, ...]
        ) -> DummyModuleList:
            captured['file_path'] = file_path
            captured['module_name'] = module_name
            captured['include_dirs'] = include_dirs
            return DummyModuleList()

    def fake_which(target: str) -> Path:
        captured['haskell_target'] = target
        return tmp_path / target / 'definition.kore'

    class DummyKDist:
        @staticmethod
        def which(target: str) -> Path:
            return fake_which(target)

    monkeypatch.setattr('kmir.kompile.kdist', DummyKDist())

    assert (
        _load_extra_module_rules(
            cast('Any', DummyKMIR()),
            f'{module_path}:TEST',
            haskell_target='custom-haskell-target',
        )
        == []
    )
    assert captured['haskell_target'] == 'custom-haskell-target'
    assert captured['file_path'] == module_path
    assert captured['module_name'] == 'TEST'
    assert captured['include_dirs'] == ((tmp_path / 'custom-haskell-target'),)
