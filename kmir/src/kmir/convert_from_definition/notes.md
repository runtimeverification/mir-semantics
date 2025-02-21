## Conventions that MIR semantics need to follow

### group(mir*) annotation
Syntax productions intended to be detected by the parser should be labeled with a group starting with `mir`: `[group(mir)]`, `[group(mir-...)]`. The group names encode information about the kind of json object a production is representing, and additionally the field names in the json object (if it has any) in the order they correspond to the sorts of the production. `---` separates the field names from the production type, `--` separates the individual group names. We use `-` to represent `_`, which is currently not allowed. E.g.,
- `mir---fieldname1--field-name-2--fieldname-3` for a production in group `mir`, with 3 field names: `fieldname1`, `field_name_2`, `fieldname_3`
- `mir-int` for a production in group `mir-int` with no field names

The following section explains the meaning of the group `mir*`.

#### mir-int
```
syntax A ::= a(Int) [group(mir-int), ...]
```
json: an integer value, e.g., `1`

#### mir-string
```
syntax A ::= a(String) [group(mir-string), ...]
```
json: a string value, e.g., `"abc"`

#### mir-bool
```
syntax A ::= a(Bool) [group(mir-bool), ...]
```
json: a boolean value, e.g., `true`

#### mir-bytes
```
syntax A ::= a(Bytes) [group(mir-bytes), ...]
```
json: an array of integer values between 0 and 255

#### mir-list
```
syntax Elems ::= List {Elem, ""} [group(mir-list), ...]
```
json: a homogeneous list, e.g. `[e1, e2, e3, ...]`, where all elements correspond to syntactic productions for the sort `Elem`.
As per naming convention, the list sort `Elems` (plural) should contain elements of sort `Elem` (singular). Usual plural formation rules (`Body -> Bodies`, `Branch -> Branches`) are respected.

#### mir-klist-ElementSort
```
syntax KL ::= List [group(mir-klist-ElementSort), ...]
```
json: a homogeneous list, e.g. `[e1, e2, e3, ...]`
Note that all elements of the json list `(e1, e2, e3)` should correspond to syntactic productions for the sort expected for the list KL, ElementSort.

#### mir-enum
```
syntax MyEnum ::= myEnumCon1(ArgSort)     [group(mir-enum)        , symbol(MyEnum::Con1)]
                | myEnumCon2(Sort1,Sort2) [group(mir-enum)        , symbol(MyEnum::Con2)]
                | myEnumCon3(field:...)   [group(mir-enum---field), symbol(MyEnum::Con3)]
                | "myEnumCon4"            [group(mir-enum)        , symbol(MyEnum::Con4)]
```
json: a dictionary with a single key-value pair.
The key should correspond to (symbol for) one of the productions for the `MyEnum` Sort, and the value should be valid json.
Arguments for variants that do not use field names are encoded as (heterogenous) _lists_ in json.
Field names can be added after `mir-enum`, separated by `---`.
Enum variants without arguments are encoded as _json strings_.

#### mir-option
```
syntax MaybeA::= someA(A) [group(mir-option)]
               | "noA"    [group(mir-option)]
```
json: represented as A would be.

#### mir-option-int, mir-option-bool, mir-option-string
Options of primitive sorts need to have the some production annotated with these group names instead, e.g.,
```
syntax MaybeInt::= someInt(Int) [group(mir-option-int)]
                | "noInt"       [group(mir-option)]
```

#### mir
Any remaining production describing MIR syntax.


### Conventions for productions
- Syntax productions with more than one non terminals should not include sorts `Int`, `Bool`, `String`, and `Bytes`, but should instead use the sorts `MIRInt`, `MIRBool`, `MIRString`, and `MIRBytes`. These are intended to be semantically equivalent, i.e.
```
mirInt(I) => I
mirBool(B) => B
mirString(S) => S
mirBytes(B) => B
```

- Similarly, productions should not directly include the List sort. They should instead use a different sort in its place, and then annotate the corresponding production with mir-klist-{ElementSort of the List}, e.g.,
```
syntax A ::= a(B, MyList) [group(mir)]
syntax MyList ::= List [group(mir-klist-MIRInt)]
```

- There are productions that correspond to enumerations

```
enum MyEnum {
  Field1,
  Field2,
}
```

These may be of the form (a)
```
syntax MyEnum ::= myEnumField1
                | myEnumField2
```
or of the form (b)
```
syntax MyEnum ::= MyEnumField1
                | MyEnumField2
syntax MyEnumField1 ::= myEnumField1
syntax MyEnumField2 ::= myEnumField2
```
We need to always have rules of form (a). This transformation has not happened yet.

### Conventions for symbols
- The symbols for the enums should be sort::value, e.g. `StatementKind::StorageLive`.

- The symbols for the terminals should also be sort::value, e.g. `Mutability::Not`. This is a terminal, but it represents a choice and therefore is also an enum.

- The symbols for the lists should  be list_sort::append, list_sort::empty, e.g. `Statements::append`, `Statements::empty`.

## Not yet handled
1. Special case parsing
We decided to not use the parser to do json processing, but to preprocess the json (or make changes at the Rust level) instead. Therefore, cases that will need to be handled include:
   - Creating unique IDs for functions (hash of function name) and alloc IDs (concatenation of alloc id and crate id). The crate id is currently included in the json file, but not expected in K AST, and the IDs might not be unique.
