from __future__ import annotations

from copy import deepcopy
import logging
from typing import TYPE_CHECKING

from pyk.kast.inner import KApply
from pyk.kast.pretty import PrettyPrinter, indent as upstream_indent

from .smir import SMIRInfo
from .ty import Ty, show_type

_LOGGER: logging.Logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pyk.kast.outer import KDefinition

def indent(text: str, size: int = 2) -> str:
    ret = []
    lines = text.split('\n')
    if len(lines) == 1:
        return lines[0]
    idx = 0
    for line in lines:
        if len(line) == 0:
            ret.append(line)
            continue
        orig_len = len(line)
        line = line.lstrip()
        orig_gap = orig_len - len(line)
        marker = f':{idx}: ' if line[0] != ':' else ''
        line = f'{' ' * (size+orig_gap)}{marker}{line}'
        ret.append(line)
        idx += 1
    return '\n'.join(ret)

def numeric_suffix(input):
    idx = None
    for i in reversed(range(len(input))):
        if input[i].isnumeric():
            idx = i
        else:
            break
    if idx:
        return input[:idx],input[idx:]
    return input,None

def strip_identical_prefix(args):
    prefix = None
    ret = []
    for arg in args:
        head,tail = numeric_suffix(arg)
        if tail is None:
            break
        elif prefix is not None:
            if head != prefix:
                prefix = None
                break
            ret.append(tail)
        else:
            prefix = head
            ret.append(tail)
    if prefix == None:
        return prefix, args
    else:
        return prefix, ret

def show_typed_value(val: str, ty: str, mut: str) -> str:
    return f'{val}:{mut} {ty}'

def show_int(val: str, width: str, negative: str) -> str:
    sign_prefix = '-' if negative == 'true' else ''
    width_suffix = '~' if width == '0' else ''
    basic_int = False
    return f'{sign_prefix}{val}{width_suffix}'

def show_subslice(_from: str, to: str, from_end: str) -> str:
    sign_prefix = '-' if from_end == 'true' else ''
    return f'.[{_from}:{sign_prefix}{to}]'

def show_const_index(offset: str, min_length: str, from_end: str) -> str:
    sign_prefix = '-' if from_end == 'true' else ''
    return f'.[{sign_prefix}{offset}]'

def show_userlist(head, tail, in_order: bool, sep='\n') -> str:
    if tail == '': return head
    if not in_order:
        head,tail = tail,head
    return f'{head}{sep}{tail}'

def show_ptr(is_ref, depth, place, mut, metadata):
    projs = ''
    if place.find('.') >= 0:
        place,projs = place.split('.',1)
        projs = '.'+projs
    sigil = '&' if is_ref else '*'
    return f'{mut}{sigil}({depth}:{place}){projs}'

def show_alloc_ref(smir, alloc_id, projs, metadata):
    # FIXME: user smir to lookup alloc
    return f'@({alloc_id}){projs}'

def show_aggregate(idx, args):
    try:
        kind = 'data' if int(idx) == 0 else 'enum'
    except:
        kind = 'enum'
    body = '' if args == '.List' else f' {{ {args.rstrip()} }}'
    return f'{kind}({idx}){body}'

def show_typed_value(val, ty, mut):
    if mut: mut = '!'
    return f'{val}:{mut}{ty}'

def show_new_local(ty,mut):
    if mut: mut = '!'
    return f'new {mut}{ty}'

def mkList(arg):
    return (indent(arg)).strip() + '\n'

def show_range_like(name, arg):
    nosort_arg = arg.replace(':Int','')
    args = [arg.strip() for arg in nosort_arg.split('\n') if len(arg) > 0]
    prefix, args = strip_identical_prefix(args)
    if prefix is not None:
        try:
            first_arg = int(args[0])
            prev_arg = first_arg
            for arg in args[1:]:
                if int(arg) == prev_arg+1:
                    prev_arg += 1
            if prev_arg == int(args[-1]):
                return f'{name}({prefix}{{{first_arg}--{prev_arg}}})'
        except:
            pass
    return f'{name}({nosort_arg.rstrip()})'

def show_ptoken_signers(arg):
    arg = arg.replace(':Int','').replace('ARG_UINT','')
    return f'Signers({arg})'

class KMIRPrettyPrinter(PrettyPrinter):
    """
    Custom Pretty Printer for improved ListItem display formatting.
    Formats ListItem elements with line breaks for better readability.
    """

    def __init__(self, definition: KDefinition, smir: SMIRInfo | None) -> None:
        """
        Initialize KMIR Pretty Printer

        Args:
            definition: K definition
        """
        super().__init__(definition)
        self.symbol_table['ListItem'] = mkList
        if smir:
            # pretty-print simple structs
            self.symbol_table['Mutability::Not'] = lambda: ''
            self.symbol_table['Mutability::Mut'] = lambda: 'mut'
            self.symbol_table['variantIdx'] = lambda val: val
            self.symbol_table['fieldIdx'] = lambda val: val
            self.symbol_table['allocId'] = lambda val: val
            self.symbol_table['local'] = lambda idx: idx

            # pretty-print more complex structs
            self.symbol_table['place'] = lambda local,projs: f'{local}{projs}'
            self.symbol_table['ty'] = lambda tyCode: show_type(smir, tyCode)
            self.symbol_table['typedValue'] = show_typed_value
            self.symbol_table['newLocal'] = show_new_local

            # pretty-print values
            self.symbol_table['Value::Integer'] = show_int
            self.symbol_table['Value::Float'] = lambda val,width: f'{val}f{width}'
            self.symbol_table['Value::BoolVal'] = lambda val: val
            self.symbol_table['Value::StringVal'] = lambda s: s
            self.symbol_table['Value::Reference'] = lambda depth,place,mut,meta: show_ptr(True,depth,place,mut,meta)
            self.symbol_table['Value::PtrLocal'] = lambda depth,place,mut,meta: show_ptr(False,depth,place,mut,meta)
            self.symbol_table['Value::AllocRef'] = lambda alloc_id,projs,metadata: show_alloc_ref(smir,alloc_id,projs,metadata)
            self.symbol_table['Value::Moved'] = lambda: 'moved'
            self.symbol_table['Value::Range'] = lambda args: show_range_like('range', args)
            self.symbol_table['Value::Aggregate'] = show_aggregate

            # projection elements list
            self.symbol_table['ProjectionElems::append'] = lambda head,tail: show_userlist(head,tail,False)
            self.symbol_table['ProjectionElems::empty'] = lambda: ''
            self.symbol_table['ProjectionElem::Subslice'] = show_subslice
            self.symbol_table['ProjectionElem::Subtype'] = lambda subty: f'.subtype({show_type(smir,subty)})'
            self.symbol_table['ProjectionElem::Downcast'] = lambda var_idx: f'.variant({var_idx})'
            self.symbol_table['ProjectionElem::OpaqueCast'] = lambda subty: f'.cast({show_type(smir,subty)})'
            self.symbol_table['ProjectionElem::Index'] = lambda local: f'.[{local}]'
            self.symbol_table['ProjectionElem::Field'] = lambda val, ty: f'.{val}'
            self.symbol_table['ProjectionElem::ConstantIndex'] = show_const_index
            self.symbol_table['ProjectionElem::Deref'] = lambda: '.*'

            # p-token specific projections
            self.symbol_table['PAccountIAcc'] = lambda: '.acct'
            self.symbol_table['PAccountIMint'] = lambda: '.mint'
            self.symbol_table['PAccountIMulti'] = lambda: '.multi'
            self.symbol_table['PAccountPRent'] = lambda: '.rent'

            # p-token specific values
            self.symbol_table['PAccount::Account'] = lambda *args: f'data AcctInfo+Acct {{ {'|'.join(args)} }}'
            self.symbol_table['PAccount::Mint'] = lambda *args: f'data AcctInfo+Mint {{ {'|'.join(args)} }}'
            self.symbol_table['PAccount::MultiSig'] = lambda *args: f'data AcctInfo+MSig {{ {'|'.join(args)} }}'
            self.symbol_table['PAccount::Rent'] =  lambda *args: f'data AcctInfo+Rent {{ {'|'.join(args)} }}'
            self.symbol_table['PToken::U8'] = lambda val: f'{val}u8'
            self.symbol_table['PToken::U64'] = lambda val: f'{val}u64'
            self.symbol_table['PToken::I32'] = lambda val: f'{val}i32'
            self.symbol_table['PToken::Key'] = lambda args: show_range_like('Key',args)
            self.symbol_table['PToken::Signers'] = show_ptoken_signers

            # pretty-print locals cell
            self.symbol_table['<locals>'] = lambda args: show_range_like('<locals>', args)

    def _print_kapply(self, kapply: KApply) -> str:
        label = kapply.label.name
        args = kapply.args
        unparsed_args = [self._print_kinner(arg) for arg in args]
        if kapply.is_cell:
            indenter = indent if label == '<locals>' else upstream_indent
            cell_contents = '\n'.join(unparsed_args).rstrip()
            cell_str = label + '\n' + indenter(cell_contents) + '\n</' + label[1:]
            return cell_str.rstrip()
        unparser = self._applied_label_str(label) if label not in self.symbol_table else self.symbol_table[label]
        return unparser(*unparsed_args)
