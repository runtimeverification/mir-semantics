# Composable Symbolic Execution 设计草案

本文档记录 `kmir prove` 的 composable symbolic execution (CSE) 设计。当前目标是先把语义边界、summary 形式、split 行为和 proof 重建方式固定下来；实现前如果设计发生变化，应先更新本文档。

## 目标

CSE 的目标是在 symbolic proof 执行到指定函数调用时，复用或生成该函数的 summary，而不是每次都从头执行 callee。

CSE 必须满足以下约束：

- `--cse-function` 指定哪些函数可以被 summary / reuse。
- `--cse-summary-store PATH` 指定 summary 的读写位置。
- CSE 需要配置合适的 function filter，使 proof 能在目标函数调用处停下。
- 目标函数调用处由 `custom_step` 接管。
- Summary 应尽量以 callee 为中心，而不是捕获整个 caller call boundary；否则 summary 很难复用于其它 caller。
- 使用 CSE 后生成的 KCFG 应保持原 proof 的 symbolic 结构。原本 callee 执行会产生 split 的地方，CSE 也应该产生 `Branch`，不能用 `NDBranch` 作为替代。
- 初始实现可以限制 `max_workers=1`，避免 summary store 读写和内部 summary proof 生成的并发一致性问题。

## 关键概念

### Call boundary

Call boundary 是主 proof 中即将执行目标函数调用的 `CTerm`。这个 state 已经包含 caller 的 continuation、当前 path constraints、实参、内存、slot store 等上下文。

如果目标函数名匹配 `--cse-function`，并且 proof 已经因为有效 `break_on_function` 规则停在该 call boundary，则 `KMIRSemantics.custom_step` 可以尝试应用 CSE。

`--cse-function` 和 `--break-on-function` 是不同概念：

- `--cse-function` 表示哪些 callee 允许使用 CSE。
- `--break-on-function` 是 backend cut-point filter。

为了避免用户重复配置，`_prove` 应把 `--cse-function` 自动并入 effective `break_on_function`，并把同一份 effective list 同时传给 kompile 和 cut-point rules。

### Callee initial state

CSE 不直接把整个 call boundary 保存成 summary initial。它先从 call boundary 中抽取目标函数执行所需的信息，构造 callee initial state。

这个 callee initial state 包含：

- callee 的函数体、locals、argument locals 和必要静态信息。
- 从 caller operands 读出的实参值。
- 与 caller state 相关但不应整体复制的 interface constraints。

reference / pointer 参数是最重要的 interface constraints 来源。对于 reference 参数，summary 不应把整个 caller stack 捕获进 initial；它应引入抽象 pointee value，并记录一个 projection 约束，说明该 reference 在 caller state 中解引用后等于这个抽象值。例如可以用如下形式表达：

```text
requires #traverseProjection(...) ==K projectionDone(..., POINTEE, ...)
```

这里的 `#traverseProjection` 参数来自 caller 中 reference 指向的 place、projection、locals/stack 信息；`POINTEE` 是 callee summary 内部使用的抽象值。这样 summary initial 保留了“callee 参数读到什么”的必要事实，但不会把 caller 的所有 locals/stack 固化进 summary。

如果 reference 是 mutable，并且 callee 可能通过它写回 caller state，summary outcome 还必须保留对应的写回关系。应用 summary 时，CSE 使用相同的 reference/projection 信息把 final 中的抽象更新写回 caller 的 post-call state。

这些 interface constraints 是 `initial` / `final` 的一部分，不单独引入新的持久化实体。

### Summary

持久化 summary 的核心形式应尽量小：

```text
Summary:
  function: string
  initial: CTerm
  outcomes: list[Outcome]
  complete: bool
  source: metadata

Outcome:
  guard: KInner
  final: CTerm
  metadata: metadata
```

其中：

- `initial` 是 abstracted callee initial state，记为 `SC`。
- `guard` 是相对于 `SC` 的 path condition，描述什么时候可以采用对应 `final`。
- `final` 是对应 guard 下的 callee final state，带有可应用回 caller 的 interface constraints。
- `metadata` 保存调试信息，例如参与生成该 outcome 的 rule labels、执行 depth、source proof node id 等。
- `complete=true` 表示 `outcomes` 的 guards 在 `SC` 下覆盖完整输入空间。
- `complete=false` 表示这些 outcomes 只覆盖部分输入空间；未覆盖部分是 remainder。
- `source` 只保存调试和复现需要的 metadata，例如 `proof_id`、创建时间、definition digest 等。

如果 summary 只有一个 outcome，`guard` 可以是 `true`。如果 summary 有多个 outcomes，每个 final 必须有自己的 guard。不能保存一个 bare `finals: list[CTerm]` 后再在 apply 时猜应该采用哪一个 final。

### Outcome guards

`guard` 是 CSE 重建 split 的最小必要信息。它来自 summary proof 中从 `SC` 到该 final 的 path condition delta。

对于 complete summary，outcome guards 必须在 `SC` 下互斥且完备：

```text
SC entails (G1 or G2 or ... or Gn)
SC entails not(Gi and Gj) for i != j
```

对于 partial summary，outcome guards 仍然必须互斥，但不要求完备。未覆盖部分由 `not(G1 or ... or Gn)` 表示。

如果无法提取稳定 guard，或者无法证明 guards 的互斥关系，则该 summary 不能用于 CSE reuse。此时应重新生成更精确的 summary，或报告 CSE 暂不支持该 proof 形状。

## CSubst 与 proof 重建

持久化 summary 不保存某次 caller 的 `CSubst`。`CSubst` 是 apply-time 结果，取决于当前 call boundary `C` 以及从它抽取出的 callee initial state。

当 `custom_step` 在当前 state `C` 尝试应用 summary case 时：

1. 先通过 function name 快速筛选。
2. 从 caller call boundary `C` 构造当前 callee initial state，记为 `CI(C)`。
3. 对候选 summary 的 `initial = SC` 做 applicability 检查。
4. 使用 pyk 的 implication / matching 能力判断 `CI(C)` 是否是 `SC` 的合法实例。

关系应表达为：

```text
CI(C) entails SC
```

也就是当前更具体的 callee initial state `CI(C)` 满足 summary pre-state `SC`。实现上可以先用结构匹配做快速失败检查，但最终 soundness gate 应使用 solver-aware check，例如 `CTermSymbolic.implies(CI(C), SC)`，并取得 apply-time `CSubst`。

得到 `CSubst` 后，将它同时应用到 outcome guard 和 final：

```text
Gi' = csubst(Gi)
CalleeFinal_i' = csubst(Fi)
```

多个 final 的选择不由 `CSubst` 单独决定，而由 instantiated guards 决定：

- 如果 `CI(C)` 蕴含某个 `Gi'`，并且其它 guards 在 `CI(C)` 下不可满足，则把 `CalleeFinal_i'` 应用回 caller call boundary，构造 post-call state，并返回 `Step(post_call_i)`。
- 如果多个 guards 在 `CI(C)` 下仍然可能成立，则返回 `Branch([G1', G2', ...])`。Branch child 会带上对应 guard；之后 custom_step 在 child state 上重新构造 `CI(C + Gi')`、重新计算 `CSubst`、重新实例化 summary，并落入唯一 outcome。
- 如果 summary 是 partial，并且 `not(G1' or ... or Gn')` 在 `CI(C)` 下可满足，则 branch constraints 还需要包含该 remainder guard。remainder branch 不使用已有 summary，而是继续生成新的 summary 或普通执行。

因此 proof reconstruction 不依赖持久化的 `CSubst`，也不依赖 hidden side table。`Branch` 只把必要的 guard 加入 child state；child state 本身包含足够信息让 CSE 再次从 caller 抽取 callee initial、重做匹配并选择 final。

这样，CSE 在 KCFG 中只生成 pyk 的正常 `Branch` 和 `Step`。它不会用 `NDBranch` 表示 deterministic split，也不需要额外保存 summary node / edge 图。

## Split 设计

CSE 的 split 来自 outcome guards，而不是来自 bare final list。

假设 summary 是：

```text
SC
  if G1 -> F1
  if G2 -> F2
```

当前 call boundary `C` 先抽取出 `CI(C)`。如果 `CI(C)` 匹配 `SC` 并得到 `csubst`，CSE 先构造：

```text
G1' = csubst(G1)
G2' = csubst(G2)
CalleeFinal1' = csubst(F1)
CalleeFinal2' = csubst(F2)
```

如果 `CI(C)` 无法直接决定 `G1'` 或 `G2'`，则在主 proof 中生成：

```text
C -- Branch[G1', G2'] --> C + G1', C + G2'
```

随后：

```text
C + G1' -- Step --> apply(C + G1', CalleeFinal1')
C + G2' -- Step --> apply(C + G2', CalleeFinal2')
```

这要求 outcome guards 在 summary initial 下互斥。否则两个 final 都可能适用，CSE 无法 soundly 选择结果。

这里的 `CalleeFinal1'` / `CalleeFinal2'` 可以在 branch child 中重新实例化得到；不需要在 `Branch` edge 上保存它们。这样生成出的 KCFG 形状接近普通 symbolic execution：先 split path condition，再在每个 path 上执行确定的一步 call-summary rewrite。

### Partial summary 与 remainder

如果已有 summary 只覆盖部分输入空间，不能直接失败后重新证明整个 `C`，否则会丢失已经可复用的部分。正确行为是生成 cover/remainder split。

Partial summary 的 coverage 是所有 outcome guards 的析取：

```text
coverage = G1 or G2 or ... or Gn
```

apply 时实例化：

```text
coverage' = csubst(coverage)
```

如果 `CI(C)` 同时可能满足 covered 和 remainder，CSE 生成：

```text
C -- Branch[G1', ..., Gn', not(coverage')] --> ...
```

其中：

- `Gi'` 分支采用已有 summary outcome。
- `not(coverage')` 分支生成新的 APRProof，证明后把新 outcome 合并回 summary store。

如果无法构造或证明 `coverage` 的 complement，不能用 `NDBranch` 兜底；应报告 CSE 暂不支持该 partial split，并回退到 normal execution 或显式失败，具体策略需要在实现前确认。

## Summary 生成范围

当当前 call boundary `C` 没有可用 summary，或者落入 partial summary 的 remainder branch 时，CSE 需要生成新的 summary。

summary proof 有两种可能的起点：

1. 从 caller call boundary 证明到 post-call frontier。
2. 从 caller 中抽取必要信息，构造 callee initial state，证明到 callee final，再将 final 的 observable effect 应用回 caller。

当前设计采用第二种。原因是第一种会把 caller continuation、caller locals/stack 以及其它 call-site 细节都带进 summary initial，summary 基本只能在非常相似的 caller state 上复用。

第二种方式的核心是：summary initial 是 callee 的抽象入口 state，但它通过 interface constraints 保留 caller 中必要的事实。reference 参数不复制整个 caller state，而是通过 `#traverseProjection` 这类约束把 caller reference 指向的值暴露给 callee summary。

应用 summary 时，CSE 从当前 caller call boundary 重建 `CI(C)`，匹配 summary initial，实例化 callee final，然后把 observable effect 应用回 caller。需要处理的 effect 包括：

- return value 写回 caller destination。
- 通过 mutable reference / pointer 发生的写回。
- callee 分配或修改的 memory / slot store 中对 caller 可见的部分。
- caller path constraints 与 callee path constraints 合并。
- panic、unreachable、stuck、vacuous 等 terminal 状态映射。

这套 application 规则必须保持尽量小，并优先复用已有 MIR runtime helper。尤其是 reference/pointer 的读写关系，应尽量通过 `#traverseProjection` / place projection 相关逻辑表达，而不是重新发明一套独立的地址模型。

生成过程：

1. 从 call boundary `C` 抽取 callee initial state。
2. 对 callee initial state 做适度抽象，得到 summary initial `SC`。
3. 从 `SC` 构造新的 APRProof。
4. 新 proof 使用同一套 CSE 配置，因此 nested callee 也可以复用或生成 summary。
5. 运行 APRProver。
6. minimize proof / KCFG。
7. 从 proof 中提取 guarded outcomes。
8. 将 summary 写入 `--cse-summary-store PATH`。
9. 回到当前 proof，按 apply 流程使用新 summary。

抽象不能过度丢失 caller path constraints。不同 caller branch 的约束不能错误共享；如果两个 caller 分支只在 path condition 或 reference pointee 条件上不同，summary initial 或 coverage guard 必须保留足够信息区分它们。

## Guard 与 coverage 提取

`guard` 应从 summary proof 中稳定提取，而不是由 final state 列表推测。

对每个 callee final `Fi`，CSE 提取从 `SC` 到 `Fi` 的 path condition delta：

1. 找到 proof 中从 summary initial node 到 `Fi` 的路径。
2. 收集路径上所有 split branch 的 `CSubst.constraints`。
3. 收集 target node 上新增的 constraints；不能只看 split edge，因为有些后端分支条件会出现在 target node 的 `cterm.constraints` 中。
4. 去掉已经由 `SC.constraints` 蕴含的约束。
5. 用 `mlAnd(...)` 得到 outcome guard `Gi`。
6. 保存 outcome `{ guard = Gi, final = Fi, metadata = ... }`。

如果同一个 final 有多条路径，可以先保留为多个 outcomes；只有在能证明合并后的 guard 等价且 finals 相同的时候，才合并为一个 outcome。

提取后必须验证：

- Feasibility: `SC + Gi` 应为 `Sat`。如果是 `Unsat`，丢弃该 outcome；如果是 `Unknown`，保守保留但不能用它证明 completeness。
- Mutual exclusion: 对任意 `i != j`，`SC + Gi + Gj` 必须为 `Unsat`。如果无法证明互斥，该 summary 不能用于 reuse。
- Coverage: `coverage = G1 or ... or Gn`。如果 `SC + not(coverage)` 为 `Unsat`，summary 是 complete；如果为 `Sat` 或 `Unknown`，summary 是 partial，remainder guard 是 `not(coverage)`。

这个 coverage/remainder 设计与 haskell-backend booster 中 rewrite rule priority group 的思路一致：coverage 是可用 case 条件的析取，remainder 是 coverage 的否定；如果 remainder unsat，则覆盖完整。

## Apply callee final to caller

CSE summary 的最终应用结果仍然是 post-call frontier：也就是目标函数调用已经返回，caller continuation 已恢复，但 caller 后续代码尚未被 summary 继续执行。

该 post-call frontier 不是直接从 summary store 中读取的完整 caller state，而是由当前 caller call boundary 和 instantiated callee final 合成：

```text
post_call = apply(C, CalleeFinal')
```

`apply` 至少负责：

- 将 callee return value 写入 caller call terminator 的 destination。
- 将 normal-return caller continuation 切到 call target basic block。
- 将 callee final 中可见的 memory / slot updates 合并回 caller。
- 对 mutable reference / pointer 参数，根据 summary initial 中的 interface constraints，把 final pointee value 写回 caller 中同一个 projection。
- 合并 callee final 的 path constraints。

stuck、vacuous、unsupported、panic、unreachable 等 terminal 分类都可以成为 summary outcomes。它们仍然需要 guard，并且在 reuse 时按同样的 split / step 规则进入对应 final state；diagnostics 作为 outcome metadata 保存。

`apply` 规则是 CSE soundness 的关键，需要先为 return value 和 reference 参数写出最小可测版本，再扩展到更多 observable effects。

## Predicate 表达与 satisfiability 检查

summary guards 统一保存为 matching-logic predicates，也就是 `CTerm.constraints` 使用的形式。

- 单个 Bool 条件 `B` 用 `mlEqualsTrue(B)` 转成 ML predicate。
- 多个 guards 的 coverage 用 `mlOr([G1, ..., Gn])` 表达。
- remainder 用 `mlNot(coverage)` 表达。
- Branch constraints 直接使用 instantiated ML predicates：`Branch([G1', ..., Gn', mlNot(coverage')])`。

不要在 summary store 中混用 Bool 层的 `notBool_` / `_orBool_` 和 ML 层的 `#Not` / `#Or`。如果需要展示或 pretty print，可以临时用 pyk 的 `ml_pred_to_bool` 转换。

satisfiability 检查应使用 backend 的 `get-model` RPC，而不是只使用 `CTermSymbolic.get_model` 的返回值。原因是 pyk 的 `CTermSymbolic.get_model` 把 `Unsat` 和 `Unknown` 都映射成 `None`，而 CSE 需要区分三种结果：

- `Sat`: 该 guard / remainder 可行。
- `Unsat`: 该 guard / remainder 不可行，可以丢弃或证明 coverage complete。
- `Unknown`: 不能证明不可行；对 coverage 来说必须当作可能 remainder，对 mutual exclusion 来说不能接受该 summary。

实现时可以在 CSE runtime 中封装一个 tri-state helper，直接调用底层 `KoreClient.get_model`，解析 `SatResult`、`UnsatResult`、`UnknownResult`。

## Summary store

`--cse-summary-store PATH` 是 CSE summary 的唯一持久化入口。推荐结构：

```text
PATH/
  manifest.json
  summaries/
    <function-hash>/
      <summary-id>.json
  proofs/
    <summary-id>/
      ...
```

`manifest.json` 保存：

- summary store version。
- definition digest / kompiled digest。
- source Rust file / SMIR digest。
- 可用函数到 summary ids 的索引。

单个 summary JSON 保存 `initial`、guarded outcomes 和 metadata。必要时可以把完整 source APRProof 保存在 `proofs/<summary-id>/`，用于调试、重新最小化和 schema migration。

outcome metadata 应至少保留 rule labels 和 depth。它们不参与 soundness 判断，但对调试 summary 生成、比较 baseline/CSE proof 结构、定位 guard 来源有用。

## custom_step 集成

`KMIRSemantics` 需要接收 CSE runtime：

```text
KMIRSemantics(
  terminate_on_thunk=...,
  cse_runtime=...
)
```

`cse_runtime` 负责：

- 识别当前 `CTerm` 是否是 CSE call boundary。
- 根据函数名查询 summary store。
- 做 applicability / coverage / split 检查。
- 启动内部 APRProof 生成 summary。
- 生成 `Step` / `Branch` 结果。
- 返回 pyk `KCFGExtendResult`。

`custom_step` 的优先级高于 normal symbolic execution。只有当 CSE 明确不接管当前 state 时，才返回 `None`，让 pyk 继续普通执行。

## 并发限制

初始实现可以要求 CSE 与 `max_workers=1` 配合使用。原因：

- summary store 读写需要事务或锁。
- 内部 summary proof 生成会读写同一个 summary store。
- parallel prover 会让多个 worker 同时生成或应用 summary，容易产生重复 proof 和覆盖写入。

如果用户启用 CSE 且 `max_workers > 1`，应直接报错，除非后续实现了 store-level locking 和 worker-safe summary generation。

## 待确认问题

- `apply(C, CalleeFinal')` 的最小实现边界，尤其是 return destination、normal target、mutable reference write-back。
- reference / pointer interface constraints 的具体 K 形状，例如 `#traverseProjection` 等式中应该使用哪些 helper、sort 和 destination。
- guard delta 提取时哪些 target-node constraints 属于 path condition，哪些只是可从 final config 推导出的派生约束。
- `Unknown` satisfiability 在实现中是否允许生成保守 remainder branch，还是直接报告 CSE unsupported。
