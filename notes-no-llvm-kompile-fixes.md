# Investigation into why the no-llvm-kompile approach is so slow

## Starting point

[Github issue 992](https://github.com/runtimeverification/mir-semantics/issues/992)
summarises the problem:
After modifying rules to avoid non-LLVM functions (transitively) in side conditions,
the execution falls back frequently and is therefore very slow.
`[preserves-definedness]` attributes are necessary but do not remove the fall-backs.

The `iterator-simple` proof (`main`) is used as a working example.

## Initial insight

The proof is run with `KORE_RPC_OPTS="-l Aborts --log-format json --log-file iter-simple-aborts.json"`
to capture information about booster aborts during rewriting.

```shell
$ KORE_RPC_OPTS="-l Aborts --log-file iter-simple-aborts.json --log-format json" uv --project kmir/ run -- kmir prove-rs --proof-dir fubar --max-iterations 100 kmir/src/tests/integration/data/prove-rs/iterator-simple.rs  --verbose --reload
...
(~3 min later)
APRProof: iterator-simple.main
    status: ProofStatus.PASSED
    admitted: False
...
```

The log file can be analysed automatically with `haskell-backend`'s tool `count-aborts` (in `.build/kore/bin` when building locally from source).
However, the tool does not show _any_ aborts, contrary to the information in the github issue.

What happens instead can be seen by inspecting the `iter-simple-aborts.json` file manually:

```shell
$ grep -C10 '"abort"' iter-simple-aborts.json
...
{"context":[{"request":"138800202871808-002"},"booster","execute",{"term":"9fc0a4b"},{"rewrite":"7e3d3e83b28c3ade778782f94db75691e8447f2b549acd5a9baa29020dbdc3c1"},"detail"],"message":"...mir-semantics/rt/data.md :  (1066, 8)"}
{"context":[{"request":"138800202871808-002"},"booster","execute",{"term":"9fc0a4b"},{"rewrite":"eadbabe1276cecb5a2ebc92bc7e96bfc3e5f7923971f77fb0d1ac37efb131909"},"detail"],"message":"KMIR-CONTROL-FLOW.program-error"}
{"context":[{"request":"138800202871808-002"},"booster","execute",{"term":"9fc0a4b"},{"rewrite":"5a859b394b3da57ce7fd26f739f06e4f274c044cddb5c1340d2ff2bc669473bf"},"detail"],"message":"RT-DATA.thunk"}
{"context":[{"request":"138800202871808-002"},"proxy"],"message":"Booster Stuck at Depth {getNat = 7}"}
{"context":[{"request":"138800202871808-002"},"proxy"],"message":"Simplifying booster state and falling back to Kore"}
{"context":[{"request":"138800202871808-002"},"proxy"],"message":"Simplifying execution state"}
{"context":[{"request":"138800202871808-002"},"proxy"],"message":"Problem with booster simplify request: Aborted - UndefinedTerm. Falling back to kore."}
{"context":[{"request":"138800202871808-002"},"proxy"],"message":"SimplifyM (using kore)"}
{"context":[{"request":"138800202871808-002"},"proxy"],"message":"Unexpected failure when calling Kore simplifier, returning original term"}
{"context":[{"request":"138800202871808-002"},"proxy"],"message":"Executing fall-back request"}
{"context":[{"request":"138800202871808-002"},"proxy","abort"],"message":"Booster and kore disagree: (Stuck,DepthBound)"}
{"context":[{"request":"138800202871808-002"},"proxy"],"message":"kore depth-bound, continuing... (currently at Depth {getNat = 8})"}
{"context":[{"request":"138800202871808-002"},"proxy"],"message":"Iterating execute request at Depth {getNat = 8}"}
{"context":[{"request":"138800202871808-002"},"booster","execute",{"term":"96c5b61"},{"rewrite":"21cdc95b5990ee262fe3d5d366f46e3e96d45da4edd4507e26b48d46df86c7de"},"detail"],"message":"RT-DATA.#setLocalValue(_,_)_RT-DATA_KItem_Place_Evaluation2-heat"}
...
```
Note the different issues here:
1. `"Booster Stuck at Depth {getNat = 7}"`: For some reason, no rule could be applied. The term is simplified and then sent to `kore` for a single rewrite step:
2. However, the simplification _fails_ due to an undefined term in booster:
   ```
"Simplifying booster state and falling back to Kore"
"Simplifying execution state"
"Problem with booster simplify request: Aborted - UndefinedTerm. Falling back to kore."
"SimplifyM (using kore)"
"Unexpected failure when calling Kore simplifier, returning original term"
```
3. The fall-back request succeeds (returning `DepthBound` at depth 1), i.e., there _is_ a (single!) rule that can be applied:
   ```
"Executing fall-back request"
"Booster and kore disagree: (Stuck,DepthBound)"
```
This pattern repeats for many rewrites, it is especially frequent for `execStmt` rules.

## Identifying the particular problem

A run with full logging enabled will produce a lot of data but can enlighten us about which particular term causes issues.
In order to reduce the log data, we can
1. require that the context starts by a _request ID_, i.e., leave out logging for the server start; and
2. only run a single request and cut execution short at depth 9, because the first booster problem arose at depth 7.

```shell
$ KORE_RPC_OPTS=" --log-file iter-simple-full-9-steps.json --log-format json --log-context request* " uv --project kmir/ run -- kmir prove-rs --proof-dir fubar  kmir/src/tests/integration/data/prove-rs/iterator-simple.rs  --verbose --reload --max-depth 9 --max-iterations 1
...
```

The log shows messages such as:

`"LLVM backend error detected: No tag found for symbol LbllookupTy8{}. Maybe attempted to evaluate a symbol with no rules?\n"`

This reports about a function `lookupTy8`, which is generated code from the optimisation to dispatch `lookupTy` to helpers according to the last digit of the argument.
These helpers _also_ need the `no-evaluators` attribute to avoid this.

```
diff --git a/kmir/src/kmir/kompile.py b/kmir/src/kmir/kompile.py
index 3ee9d7de..827ecdad 100644
--- a/kmir/src/kmir/kompile.py
+++ b/kmir/src/kmir/kompile.py
@@ -355,6 +355,7 @@ def _make_stratified_rules(
             attrs=(
                 App('function'),
                 App('total'),
+                App('no-evaluators'),  # HS backend only
             ),
         )
         for i in range(strata)
```

## Next issue: `rvalueNullaryOp` rules

After applying the above fix, the proof for `iterator-simple` was _failing_ because of two stuck nodes. The reason was evident from looking at the proof tree.

In both cases, the `rvalueNullaryOp` rules led to a non-deterministic branch because of two matching rules, one for `nullOpUbChecks` (unconditionally `false`), and another rule introduced by the `#resolvedNullaryOp` refactoring.

The easiest fix was to revert the changes to the `NullaryOp` rules.
Having `lookupTy(TY)` in the side condition is not a problem, and the `#sizeOf(lookupTy(TY))` (and `#alignOf(..)` respectively) won't lead to problems.

```
diff --git a/kmir/src/kmir/kdist/mir-semantics/rt/data.md b/kmir/src/kmir/kdist/mir-semantics/rt/data.md
index f782177b..c476b8c2 100644
--- a/kmir/src/kmir/kdist/mir-semantics/rt/data.md
+++ b/kmir/src/kmir/kdist/mir-semantics/rt/data.md
@@ -2377,27 +2377,18 @@ This information is read from the layout in the `TypeInfo` if available, or a fi

 ```k
 // FIXME: 64 is hardcoded since usize not supported
-  syntax KItem ::= #resolvedNullaryOp( NullOp , Ty , TypeInfo )
-
-  rule <k> rvalueNullaryOp(OP, TY)
-        => #resolvedNullaryOp(OP, TY, lookupTy(TY))
-       ...
-       </k>
-    [preserves-definedness]
-
-  rule <k> #resolvedNullaryOp(nullOpSizeOf, _TY, TYINFO)
-        => Integer(#sizeOf(TYINFO), 64, false)
-       ...
-       </k>
-    requires TYINFO =/=K typeInfoVoidType
-    [preserves-definedness]
-
-  rule <k> #resolvedNullaryOp(nullOpAlignOf, _TY, TYINFO)
-        => Integer(#alignOf(TYINFO), 64, false)
-       ...
-       </k>
-    requires TYINFO =/=K typeInfoVoidType
-    [preserves-definedness]
+rule <k> rvalueNullaryOp(nullOpSizeOf, TY)
+      =>
+           Integer(#sizeOf(lookupTy(TY)), 64, false)
+         ...
+     </k>
+    requires lookupTy(TY) =/=K typeInfoVoidType
+rule <k> rvalueNullaryOp(nullOpAlignOf, TY)
+      =>
+           Integer(#alignOf(lookupTy(TY)), 64, false)
+         ...
+     </k>
+    requires lookupTy(TY) =/=K typeInfoVoidType
 ```

 `nullOpOffsetOf(VariantAndFieldIndices)`
```

## Next issues: Integration test failures

After applying the above revert, the `iterator-simple` proof succeeded in 8 seconds.
Some other integration tests are failing, though:

* Unexpectedly-failing proofs:

| iter-eq-copied-take-dereftruncate] (repro) | assert False | Special projection rule (transparent cast) does not fire |
| iter_next_1]                               | assert False | Special projection rule (transparent cast) does not fire |
| spl-multisig-iter-eq-copied-next] (repro)  | assert False | Special projection rule (transparent cast) does not fire |
| iter_next_2]                               | assert False | Special projection rule (transparent cast) does not fire |

Failing tests from the future:

| closure_access_struct]                     | assert False | `#resolvedRvalueRefZS` issue                             |
| closure-staged]                            | assert False | `#resolvedRvalueRefZS` issue                             |

* Problems with stuck nodes in expected proof trees (for failing proofs)

| interior-mut3-fail]     | AssertionError: The actual output does not match the expected output: | Suspected problem with castTransmute |
| ref-ptr-cast-elem-fail] | AssertionError: The actual output does not match the expected output: | Suspected problem with castTransmute |

* Harmless step count updates causing failures

| niche-enum]                    | AssertionError: The actual output does not match the expected output: | Harmless, step count update required                     |
| symbolic-structs-fail]         | AssertionError: The actual output does not match the expected output: | Harmless, step count update required                     |
| test_offset_from-fail]         | AssertionError: The actual output does not match the expected output: | Harmless, step count update required                     |
| pointer-cast-length-test-fail] | AssertionError: The actual output does not match the expected output: | Harmless, step count update required                     |
| iterator-simple]               | AssertionError: The actual output does not match the expected output: | Harmless step count update, removing intermediate state  |
| symbolic-args-fail]            | AssertionError: The actual output does not match the expected output: | Harmless, step count update required                     |
| interior-mut-fail]             | AssertionError: The actual output does not match the expected output: | Harmless, step count update, removing intermediate state |

### `cast` Problems in failing proofs

The new symbol `#resolvedCastTransmute` is not defined with sort `Evaluation`,
therefore the evaluation does not `thunk` but gets stuck instead.

This affects `interior-mut3-fail` and `ref-ptr-cast-elem-fail`:
The execution gets stuck where a pointer alignment is checked,
at the cast from a unit pointer (`*const()`) to a `usize`.
Before the change, a thunk was created and then checked (after a few more operations).

### Problems with `Aggregate` wrapper in iteration code

The (current) problem in `iter_next_1` appears to be that an `Aggregate`
wrapper is created around a list to index into (for the `iter`).
This `Aggregate` does not conform to the types given to the locals involved,
and is most likely created by an erratic `ProjectionElemWrapStruct`.
It is unclear where exactly, and why, that projections is created around the list,
it should have been created around a pointer to it (a `NonNull` wrapper).
Similar problem appear in `iter_next_2`, `iter-eq-copied-...`, and `spl-multisig-...`.

The code involved in this wrapper projection is very complex, and there may
have been a problem converting it to avoid the unevaluated functions.

### `#resolvedRvalueRefZS` problems

The `#resolvedRvalueRefZS` rewrite does not fire when a reference to a function is created.
The simple reason is that the `#zeroSizedType` is `false` for function types. It should return `true`
(the two tests failing with this error came from a commit after the initial version of the branch).

# Re-doing the no-llvm transformation

The K code here has been transformed to always evaluate the `lookupTy`
and `lookupAlloc` and `lookupFunction` separately, without nesting any
other functions.
However, the actual problem with the HS-only evaluation was different:
Any function call that LLVM backend would _evaluate to_ an expression
which calls a HS-only lookup function would crash the LLVM library (and the server).

Instead of eliminating all lookup functions from rewrite rules, one should make
the functions that internally use these lookup functions also HS-only.
The prime example was `#getBlocks`, which internally calls `lookupFunction`:

```
rule #getBlocks(TY) => #getBlocksAux(lookupFunction(TY))
```
Rather than the massive refactoring of rewrite rules, one should target such _functions_.
