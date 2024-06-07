### Tasks

1. Items created from crate imports should be Int (Question answered in meeting). Addressed. I list the relevant items below.
```
// In ty.k. (imported from crate)
syntax AdtDef
// In ty.k. (imported from crate)
syntax AliasDef
// In ty.k. (imported from crate)
syntax BrNamedDef
// In ty.k. (imported from crate)
syntax ClosureDef
// In ty.k. (imported from crate)
syntax ConstDef
// In ty.k. (imported from crate)
syntax CoroutineDef
// In ty.k. (imported from crate)
syntax CoroutineWitnessDef
// In body.k. Initially, from lib.rs. (imported from crate)
syntax CrateItem
// In ty.k. (imported from crate)
syntax FnDef
// In ty.k. (imported from crate)
syntax ForeignDef
// In ty.k. (imported from crate)
syntax ForeignModuleDef
// In ty.k. (imported from crate)
syntax GenericDef
// In ty.k. (imported from crate)
syntax ImplDef
// In ty.k. (imported from crate)
syntax ParamDef
// In ty.k. (imported from crate)
syntax RegionDef
// In mono.k. (imported from crate)
syntax StaticDef
// In ty.k. (imported from crate)
syntax TraitDef
```

2. `RangeInclusive<T>` is just a pair (inclusive of its ends), so we know how to interpret it. See the Rust compiler src for its definition. (Question answered in meeting). Addressed.
```
// In abi.k, from abi.rs.
syntax RangeInclusiveForVariantIdx
```

3. Currently, these are organised exactly as they appear in the stable MIR AST document. Separate in files, organize modules. Look at the MIR semantics files organization for a start point. TODO.

4. Update AST based on updated/finalied json format. As far as we know, one change will be that some of the interned values (appearing as ints) will be materialized).

### Comments

- The names used for the K AST are as close to the names from the stable MIR document as possible. I have made the following changes.
  - Changed snake case to camel case, since underscore would be problematic in the K definition.
  - Prepended the defined Sort name to all the terninals, non terminals, and constructors associated with a Sort. That was in order to make sure they were unique, since many of the names in the stable MIR AST were not.
  - When creating a Sort for an option for a type, I prepend Maybe to the name, and some and no to the constructors.
  - When creating a vector<T>, I use the plural of T or append List at the end.

- The root seems to be the Body, so anything unreacable from there is probably not needed. But, for now, we plan to continue to include unused items, and will delete or comment out when we are sure that they will not be included at a later time (e.g., after interning is completed, ...).

- In the stable MIR AST, there are type aliases (e.g., `pub type BasicBlockIdx = usize;`), or named structs that are created to simply represent another type (e.g., `pub struct AllocId(usize);`). Let `T1` be the original type and `T2` be the alias or named struct type.
  We discussed (in the meeting - 05/30/2024) if after the definition of `T2`, `T2` would be consistently used (in place of `T1`) everywhere in the AST structures, or if there might be places that uses of `T1` might exist when `T2` was intended. I brought up the question thinking of the following scenario:

```
pub struct Size = u32;
```
  This would lead us to write something like syntax `Size ::= Int`, or `syntax Size ::= size(Int)`

  Two constructs that both need the size, one of them using Size and the other u32.
```
pub struct ArrayTy {
  pub elTy: Ty,
  pub size: Size,
}
pub struct Allocation {
  pub ptr: Int,
  pub size: u32,
}
```
  These would become
```
syntax ArrayTy ::= arrayTy(elTy: Ty, size: Size)
syntax Allocation ::= allocation(ptr: Int, size: Int)
```
  potentially leading to difficulties in propagating the size variable through the semantics, stemming right from the translation of the AST into K records.

  We decided that this is unlikely to happen. If it does, we will fix it in the semantics, als also maybe send a bug report, since the use of `T1` rathter than `T2` wwould be unintentional.

- There are variables defined with type int or string, that I have chosen to define as a ctor(int) or ctor(string), in order to make clear where the correspoding K sort is allowed to match. That is a choice we can evaluate and change later on.
  For now, I have defined several sorts as ctor(Int) or ctor(Opaque) or ctor(String) instead of simply Int or String or Opaque (generally, T2 ::= t2(T1) rather than T2 ::= T1, for T1 one of Int, String, Opaque).
  I have made this choice in several places (though not consistently, e.g., not for the Sorts imported from crates) in order to make it clear where the corresponding K sort should match, and make inference easier. This seems too burdensome or verbose though, because there are many used in few/single locations. We can evaluate this choice as we go.

- Lists of any items. I have currently assumed no separators, TBD and easily changed. For that reason, I always include constructors in pairs and no infix syntax. json should also help with having no ambiguities: since lists have clear start and end, list items at the K level should be clear.

