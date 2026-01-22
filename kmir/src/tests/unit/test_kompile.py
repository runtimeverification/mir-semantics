from __future__ import annotations

from pyk.kore.syntax import And, App, Axiom, EVar, Rewrites, SortApp, Top

from kmir.kompile import _add_exists_quantifiers, _collect_evars


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
