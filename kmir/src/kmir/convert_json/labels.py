###----------------------------------------------------------------------------
# Information about the KMIR AST definition
# For demonstration - testing - prototype purpose only. We should be able to
# extract there and create dict definition_dict from the K definition.

# module names
module_body = "BODY"
#...

# sort names
terminatorKindCallSort = "TerminatorKindCall"
operandSort = "Operand"
operandsSort = "Operands"
placeSort = "Place"
maybeBasicBlockIdxSort = "MaybeBasicBlockIdx"
unwindActionSort = "UnwindAction"
#...

# dictionary with information about the constructors in the K AST
# - sort of the generated term
# - module this belongs to
# - a list, containing the sorts of the arguments to this constructor
# This may need to change, in order to handle List.
definition_dict = {
"terminatorKindCall" : { "sort" : terminatorKindCallSort, "module" : module_body, "argSorts" : [operandSort, operandsSort, placeSort, maybeBasicBlockIdxSort, unwindActionSort]}
#...
}

### END information about the KMIR AST definition
#------------------------------------------------------------------------------

# Functions to create labels
def arity(s: str) -> int:
  return len(definition_dict[s]["argSorts"])

def klabel(s: str) -> str:
  a = arity(s)
  p = "" if a  == 0 else "(" + "_,"*(a-1) + "_)"
  v = definition_dict[s]
  l = [s+p, v["module"], v["sort"]]
  l.extend(v["argSorts"])
  label = "_".join(l)
  return label

