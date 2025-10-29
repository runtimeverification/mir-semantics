from __future__ import annotations

import logging
from itertools import count
from typing import TYPE_CHECKING, NamedTuple

from pyk.kast.inner import KApply, KSort, KVariable, Subst, build_cons
from pyk.kast.manip import free_vars, split_config_from
from pyk.kast.prelude.collections import list_empty, list_of
from pyk.kast.prelude.kint import eqInt, leInt
from pyk.kast.prelude.ml import mlEqualsTrue
from pyk.kast.prelude.utils import token

from .ty import ArrayT, BoolT, EnumT, IntT, PtrT, RefT, StructT, TupleT, Ty, UintT, UnionT
from .value import (
    NO_SIZE,
    AggregateValue,
    BoolValue,
    DynamicSize,
    IntValue,
    Local,
    Metadata,
    Place,
    PtrEmulationFromMetadata,
    PtrLocalValue,
    RangeValue,
    RefValue,
    StaticSize,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping, Sequence
    from random import Random
    from typing import Any, Final

    from pyk.kast import KInner
    from pyk.kast.outer import KDefinition

    from .smir import SMIRInfo
    from .ty import TypeMetadata
    from .value import MetadataSize, Value


_LOGGER: Final = logging.getLogger(__name__)


RANDOM_MAX_ARRAY_LEN: Final = 32


LOCAL_0: Final = KApply('newLocal', KApply('ty', token(0)), KApply('Mutability::Not'))


class ConcreteMode(NamedTuple): ...


class SymbolicMode(NamedTuple): ...


class RandomMode(NamedTuple):
    random: Random


CallConfigMode = ConcreteMode | SymbolicMode | RandomMode


class CallConfig(NamedTuple):
    config: KInner
    constraints: tuple[KInner, ...]


def make_call_config(
    definition: KDefinition,
    *,
    smir_info: SMIRInfo,
    start_symbol: str,
    mode: CallConfigMode,
) -> CallConfig:
    fn_data = _FunctionData.load(smir_info=smir_info, start_symbol=start_symbol)
    match mode:
        case ConcreteMode():
            config = _make_concrete_call_config(
                definition=definition,
                fn_data=fn_data,
            )
            return CallConfig(config=config, constraints=())
        case SymbolicMode():
            config, constraints = _make_symbolic_call_config(
                definition=definition,
                fn_data=fn_data,
                types=smir_info.types,
            )
            return CallConfig(config=config, constraints=tuple(constraints))
        case RandomMode(random):
            config = _make_random_call_config(
                definition=definition,
                fn_data=fn_data,
                types=smir_info.types,
                random=random,
            )
            return CallConfig(config=config, constraints=())


class _FunctionData(NamedTuple):
    symbol: str
    target: int
    args: tuple[_Local, ...]

    @staticmethod
    def load(*, smir_info: SMIRInfo, start_symbol: str) -> _FunctionData:
        try:
            target = smir_info.function_tys[start_symbol]
        except KeyError as err:
            raise ValueError(f'{start_symbol} not found in program') from err

        raw_args = smir_info.function_arguments[start_symbol]
        args = tuple(_Local.from_raw(arg) for arg in raw_args)
        return _FunctionData(symbol=start_symbol, target=target, args=args)

    @property
    def call_terminator(self) -> KInner:
        return mk_call_terminator(target=self.target, arg_count=len(self.args))


class _Local(NamedTuple):
    ty: Ty
    mut: bool

    @staticmethod
    def from_raw(data: Any) -> _Local:
        match data:
            case {
                'ty': ty,
                'mutability': 'Mut' | 'Not' as mut,
            }:
                return _Local(ty=Ty(ty), mut=mut == 'Mut')
            case _:
                raise ValueError(f'Cannot parse as _Local: {data}')


def _make_concrete_call_config(
    *,
    definition: KDefinition,
    fn_data: _FunctionData,
) -> KInner:
    if fn_data.args:
        raise ValueError(f'Cannot create concrete call configuration for {fn_data.symbol}: function has parameters')

    return _make_concrete_call_config_with_locals(
        definition=definition,
        fn_data=fn_data,
        localvars=[],
    )


def _make_random_call_config(
    *,
    definition: KDefinition,
    fn_data: _FunctionData,
    types: Mapping[Ty, TypeMetadata],
    random: Random,
) -> KInner:
    localvars = _random_locals(random, fn_data.args, types)
    return _make_concrete_call_config_with_locals(
        definition=definition,
        fn_data=fn_data,
        localvars=localvars,
    )


def _make_concrete_call_config_with_locals(
    *,
    definition: KDefinition,
    fn_data: _FunctionData,
    localvars: list[KInner],
) -> KInner:
    def init_subst() -> dict[str, KInner]:
        init_config = definition.init_config(KSort('GeneratedTopCell'))
        _, res = split_config_from(init_config)
        return res

    # The configuration is the default initial configuration, with the K cell updated with the call terminator
    # TODO: see if this can be expressed in more simple terms
    subst = Subst(
        {
            **init_subst(),
            **{
                'K_CELL': fn_data.call_terminator,
                'LOCALS_CELL': list_of(localvars),
            },
        }
    )
    empty_config = definition.empty_config(KSort('GeneratedTopCell'))
    config = subst(empty_config)
    assert not free_vars(config), f'Config by construction should not have any free variables: {config}'
    return config


def _make_symbolic_call_config(
    *,
    definition: KDefinition,
    fn_data: _FunctionData,
    types: Mapping[Ty, TypeMetadata],
) -> tuple[KInner, list[KInner]]:
    locals, constraints = _symbolic_locals(fn_data.args, types)
    subst = Subst(
        {
            'K_CELL': fn_data.call_terminator,
            'STACK_CELL': list_empty(),  # FIXME see #560, problems matching a symbolic stack
            'LOCALS_CELL': list_of(locals),
        },
    )
    empty_config = definition.empty_config(KSort('GeneratedTopCell'))
    config = subst(empty_config)
    return config, constraints


def int_var(var: KVariable, num_bytes: int, signed: bool) -> tuple[KInner, Iterable[KInner]]:
    bit_width = num_bytes * 8
    var_max = ((1 << (bit_width - 1)) if signed else (1 << bit_width)) - 1
    var_min = -(1 << (bit_width - 1)) if signed else 0
    constraints = (mlEqualsTrue(leInt(var, token(var_max))), mlEqualsTrue(leInt(token(var_min), var)))
    term = KApply('Value::Integer', (var, token(bit_width), token(signed)))
    return term, constraints


def bool_var(var: KVariable) -> tuple[KInner, Iterable[KInner]]:
    term = KApply('Value::BoolVal', (var,))
    return term, ()


def mk_call_terminator(target: int, arg_count: int) -> KInner:
    operands = [
        KApply(
            'Operand::Copy',
            (KApply('place', (KApply('local', (token(i + 1),)), KApply('ProjectionElems::empty', ()))),),
        )
        for i in range(arg_count)
    ]

    args = build_cons(KApply('Operands::empty', ()), 'Operands::append', operands)

    return KApply(
        '#execTerminator(_)_KMIR-CONTROL-FLOW_KItem_Terminator',
        (
            KApply(
                'terminator(_,_)_BODY_Terminator_TerminatorKind_Span',
                (
                    KApply(
                        'TerminatorKind::Call',
                        (
                            KApply(
                                'Operand::Constant',
                                (
                                    KApply(
                                        'constOperand(_,_,_)_BODY_ConstOperand_Span_MaybeUserTypeAnnotationIndex_MirConst',
                                        (
                                            KApply('span', token(0)),
                                            KApply('noUserTypeAnnotationIndex_BODY_MaybeUserTypeAnnotationIndex', ()),
                                            KApply(
                                                'mirConst(_,_,_)_TYPES_MirConst_ConstantKind_Ty_MirConstId',
                                                (
                                                    KApply('ConstantKind::ZeroSized', ()),
                                                    KApply('ty', (token(target),)),
                                                    KApply('mirConstId(_)_TYPES_MirConstId_Int', (token(0),)),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                            args,
                            KApply(
                                'place',
                                (
                                    KApply('local', (token(0),)),
                                    KApply('ProjectionElems::empty', ()),
                                ),
                            ),
                            KApply('noBasicBlockIdx_BODY_MaybeBasicBlockIdx', ()),
                            KApply('UnwindAction::Continue', ()),
                        ),
                    ),
                    KApply('span', token(0)),
                ),
            ),
        ),
    )


def _symbolic_locals(args: Sequence[_Local], types: Mapping[Ty, TypeMetadata]) -> tuple[list[KInner], list[KInner]]:
    localvars, constraints = _ArgGenerator(types).run(args)
    return ([LOCAL_0] + localvars, constraints)


class _ArgGenerator:
    types: Mapping[Ty, TypeMetadata]
    locals: list[KInner]
    pointees: list[KInner]
    constraints: list[KInner]
    counter: int
    ref_offset: int

    if TYPE_CHECKING:
        from .smir import Ty

    def __init__(self, types: Mapping[Ty, TypeMetadata]) -> None:
        self.types = types
        self.locals = []
        self.pointees = []
        self.constraints = []
        self.counter = 1
        self.ref_offset = 0

    def run(self, local_types: Sequence[_Local]) -> tuple[list[KInner], list[KInner]]:
        self.ref_offset = len(local_types) + 1
        for ty, mut in local_types:
            self._add_local(ty, mut)
        return (self.locals + self.pointees, self.constraints)

    def _add_local(self, ty: Ty, mutable: bool) -> None:
        value, constraints, _ = self._symbolic_value(ty, mutable)

        self.locals.append(_typed_value(value, ty, mutable))
        self.constraints += constraints

    def _fresh_var(self, prefix: str) -> KVariable:
        name = prefix + str(self.counter)
        self.counter += 1
        return KVariable(name)

    def _symbolic_value(self, ty: Ty, mutable: bool) -> tuple[KInner, Iterable[KInner], KInner | None]:
        # returns: symbolic value of given type, related constraints, related pointer metadata

        ptr_emulation_label = 'ptrEmulation(_)_RT-VALUE-SYNTAX_PtrEmulation_Metadata'

        no_metadata = KApply(
            'Metadata',
            KApply('noMetadataSize', ()),
            token(0),
            KApply('noMetadataSize', ()),
        )

        match self.types.get(ty):
            case IntT(info):
                val, constraints = int_var(self._fresh_var('ARG_INT'), info.value, True)
                return val, constraints, None

            case UintT(info):
                val, constraints = int_var(self._fresh_var('ARG_UINT'), info.value, False)
                return val, constraints, None

            case BoolT():
                val, constraints = bool_var(self._fresh_var('ARG_BOOL'))
                return val, constraints, None

            case EnumT(_, _, discriminants):
                variant_var = self._fresh_var('ARG_VARIDX')
                # constraints for variant index being in range
                max_variant = len(discriminants)
                idx_range = [
                    mlEqualsTrue(leInt(token(0), variant_var)),
                    mlEqualsTrue(leInt(variant_var, token(max_variant))),
                ]
                args = self._fresh_var('ENUM_ARGS')
                return KApply('Value::Aggregate', (KApply('variantIdx', (variant_var,)), args)), idx_range, None

            case StructT(_, _, fields):
                field_vars: list[KInner] = []
                field_constraints: list[KInner] = []
                for _ty in fields:
                    new_var, new_constraints, _ = self._symbolic_value(_ty, mutable)
                    field_vars.append(new_var)
                    field_constraints += new_constraints
                return (
                    KApply('Value::Aggregate', (KApply('variantIdx', (token(0),)), list_of(field_vars))),
                    field_constraints,
                    None,
                )

            case UnionT():
                args = self._fresh_var('ARG_UNION')
                return KApply('Value::Aggregate', (KApply('variantIdx', (token(0),)), args)), [], None

            case ArrayT(_, None):
                elems = self._fresh_var('ARG_ARRAY')
                l = self._fresh_var('ARG_ARRAY_LEN')
                return (
                    KApply('Value::Range', (elems,)),
                    [mlEqualsTrue(eqInt(KApply('sizeList', (elems,)), l))],
                    KApply(
                        'Metadata',
                        (
                            KApply('dynamicSize', (l,)),
                            token(0),
                            KApply('dynamicSize', (l,)),
                        ),
                    ),
                )

            case ArrayT(element_type, size) if size is not None:
                elem_vars: list[KInner] = []
                elem_constraints: list[KInner] = []
                for _ in range(size):
                    new_var, new_constraints, _ = self._symbolic_value(element_type, mutable)
                    elem_vars.append(new_var)
                    elem_constraints += new_constraints
                return (
                    KApply('Value::Range', (list_of(elem_vars),)),
                    elem_constraints,
                    KApply(
                        'Metadata',
                        (
                            KApply('staticSize', (token(size),)),
                            token(0),
                            KApply('staticSize', (token(size),)),
                        ),
                    ),
                )

            case TupleT(components):
                elem_vars = []
                elem_constraints = []
                for _ty in components:
                    new_var, new_constraints, _ = self._symbolic_value(_ty, mutable)
                    elem_vars.append(new_var)
                    elem_constraints += new_constraints
                return (
                    KApply('Value::Aggregate', (KApply('variantIdx', (token(0),)), list_of(elem_vars))),
                    elem_constraints,
                    None,
                )

            case RefT(pointee_ty):
                pointee_var, pointee_constraints, metadata = self._symbolic_value(pointee_ty, mutable)
                ref = self.ref_offset
                self.ref_offset += 1
                self.pointees.append(_typed_value(pointee_var, pointee_ty, mutable))
                return (
                    KApply(
                        'Value::Reference',
                        (
                            token(0),  # Stack OFFSET field
                            KApply('place', (KApply('local', (token(ref),)), KApply('ProjectionElems::empty', ()))),
                            KApply('Mutability::Mut', ()) if mutable else KApply('Mutability::Not', ()),
                            metadata if metadata is not None else no_metadata,
                        ),
                    ),
                    pointee_constraints,
                    None,
                )
            case PtrT(pointee_ty):
                pointee_var, pointee_constraints, metadata = self._symbolic_value(pointee_ty, mutable)
                ref = self.ref_offset
                self.ref_offset += 1
                self.pointees.append(_typed_value(pointee_var, pointee_ty, mutable))
                ptr_meta = metadata if metadata is not None else no_metadata
                return (
                    KApply(
                        'Value::PtrLocal',
                        (
                            token(0),
                            KApply('place', (KApply('local', (token(ref),)), KApply('ProjectionElems::empty', ()))),
                            KApply('Mutability::Mut', ()) if mutable else KApply('Mutability::Not', ()),
                            KApply(ptr_emulation_label, (ptr_meta,)),
                        ),
                    ),
                    pointee_constraints,
                    None,
                )
            case other:
                _LOGGER.warning(f'Missing type information ({other}) for type {ty}')
                # missing type information, but can assert that this is a value
                var = self._fresh_var('ARG')
                return var, [mlEqualsTrue(KApply('isValue', (var,)))], None


def _typed_value(value: KInner, ty: int, mutable: bool) -> KInner:
    return KApply(
        'typedValue',
        (value, KApply('ty', (token(ty),)), KApply('Mutability::Mut' if mutable else 'Mutability::Not', ())),
    )


class TypedValue(NamedTuple):
    value: Value
    ty: Ty
    mut: bool

    @staticmethod
    def from_local(value: Value, local: _Local) -> TypedValue:
        return TypedValue(value=value, ty=local.ty, mut=local.mut)

    def to_kast(self) -> KInner:
        return _typed_value(value=self.value.to_kast(), ty=self.ty, mutable=self.mut)


def _random_locals(random: Random, args: Sequence[_Local], types: Mapping[Ty, TypeMetadata]) -> list[KInner]:
    return _RandomArgGen(random=random, args=args, types=types).run()


class SimpleRes(NamedTuple):
    value: TypedValue


class ArrayRes(NamedTuple):
    value: TypedValue
    metadata_size: MetadataSize


RandomValueRes = SimpleRes | ArrayRes


class _RandomArgGen:
    _random: Random
    _args: Sequence[_Local]
    _types: Mapping[Ty, TypeMetadata]
    _pointees: list[TypedValue]
    _ref: Iterator[int]

    def __init__(self, *, random: Random, args: Sequence[_Local], types: Mapping[Ty, TypeMetadata]):
        self._random = random
        self._args = args
        self._types = types
        self._pointees = []
        self._ref = count(len(args) + 1)

    def run(self) -> list[KInner]:
        res: list[KInner] = [LOCAL_0]
        res.extend(self._random_value(arg).value.to_kast() for arg in self._args)
        res.extend(pointee.to_kast() for pointee in self._pointees)
        return res

    def _random_value(self, local: _Local) -> RandomValueRes:
        try:
            type_info = self._types[local.ty]
        except KeyError as err:
            raise ValueError(f'Unknown type: {local.ty}') from err

        match type_info:
            case BoolT():
                return SimpleRes(
                    TypedValue.from_local(
                        value=self._random_bool_value(),
                        local=local,
                    )
                )
            case IntT() | UintT():
                return SimpleRes(
                    TypedValue.from_local(
                        value=self._random_int_value(type_info),
                        local=local,
                    ),
                )
            case EnumT(discriminants=discriminants, fields=fields):
                return SimpleRes(
                    TypedValue.from_local(
                        value=self._random_enum_value(mut=local.mut, discriminants=discriminants, fields=fields),
                        local=local,
                    ),
                )
            case StructT(fields=tys) | TupleT(components=tys):
                return SimpleRes(
                    TypedValue.from_local(
                        value=self._random_struct_or_tuple_value(mut=local.mut, tys=tys),
                        local=local,
                    ),
                )
            case ArrayT(element_type=elem_ty, length=length):
                value, metadata_size = self._random_array_value(mut=local.mut, elem_ty=elem_ty, length=length)
                return ArrayRes(
                    value=TypedValue.from_local(
                        value=value,
                        local=local,
                    ),
                    metadata_size=metadata_size,
                )
            case PtrT() | RefT():
                return SimpleRes(
                    value=TypedValue.from_local(
                        value=self._random_ptr_value(mut=local.mut, type_info=type_info),
                        local=local,
                    ),
                )
            case _:
                raise ValueError(f'Type unsupported for random value generator: {type_info}')

    def _random_bool_value(self) -> BoolValue:
        return BoolValue(bool(self._random.getrandbits(1)))

    def _random_int_value(self, type_info: IntT | UintT) -> IntValue:
        return IntValue(
            value=self._random.randint(type_info.min, type_info.max),
            nbits=type_info.nbits,
            signed=isinstance(type_info, IntT),
        )

    def _random_enum_value(
        self,
        *,
        mut: bool,
        discriminants: list[int],
        fields: list[list[Ty]],
    ) -> AggregateValue:
        variant_idx = self._random.randrange(len(discriminants))
        values = self._random_fields(tys=fields[variant_idx], mut=mut)
        return AggregateValue(variant_idx, values)

    def _random_struct_or_tuple_value(self, *, mut: bool, tys: list[Ty]) -> AggregateValue:
        return AggregateValue(0, fields=self._random_fields(tys=tys, mut=mut))

    def _random_fields(self, *, tys: list[Ty], mut: bool) -> tuple[Value, ...]:
        return tuple(self._random_value(local=_Local(ty=ty, mut=mut)).value.value for ty in tys)

    def _random_array_value(self, *, mut: bool, elem_ty: Ty, length: int | None) -> tuple[RangeValue, MetadataSize]:
        metadata_size: MetadataSize
        if length is None:
            length = self._random.randint(0, RANDOM_MAX_ARRAY_LEN)
            metadata_size = DynamicSize(length)
        else:
            metadata_size = StaticSize(length)

        elems = tuple(self._random_value(local=_Local(ty=elem_ty, mut=mut)).value.value for _ in range(length))
        value = RangeValue(elems)
        return value, metadata_size

    def _random_ptr_value(self, mut: bool, type_info: PtrT | RefT) -> PtrLocalValue | RefValue:
        pointee_local = _Local(ty=type_info.pointee_type, mut=mut)
        pointee_res = self._random_value(pointee_local)
        self._pointees.append(pointee_res.value)

        metadata_size: MetadataSize
        match pointee_res:
            case ArrayRes(metadata_size=metadata_size):
                pass
            case _:
                metadata_size = NO_SIZE

        metadata = Metadata(size=metadata_size, pointer_offset=0, origin_size=metadata_size)
        emulation = PtrEmulationFromMetadata(metadata)

        ref = next(self._ref)

        match type_info:
            case PtrT():
                return PtrLocalValue(
                    stack_depth=0,
                    place=Place(local=Local(ref)),
                    mut=mut,
                    emulation=emulation,
                )
            case RefT():
                return RefValue(
                    stack_depth=0,
                    place=Place(local=Local(ref)),
                    mut=mut,
                    metadata=metadata,
                )
            case _:
                raise AssertionError()
