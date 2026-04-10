# Success Criteria Coverage: Challenge 0013

This table tracks coverage against the published Challenge 13 bar. Status
values are intentionally coarse so the PR description and README can point to a
single source of truth.

Status legend:

- `not started`: no branch-local spec or proof entrypoint yet
- `harness defined`: a branch-local artifact exists, but no concrete frontier
  has been recorded yet
- `frontier reached`: a proof/repro entrypoint exists and reduces to a concrete
  stuck/failing frontier
- `blocked`: the entrypoint exists, but a precise blocker prevents further
  progress
- `passed`: the entrypoint has been discharged on this branch

| Function | Upstream Location | Harness/Spec File | Start Symbol | Kind | Status | Blocker Class | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Invariant` for `CStr` | `library/core/src/ffi/c_str.rs` | `—` | `—` | invariant | `not started` | `UNKNOWN` | No branch-local invariant spec has been introduced yet. |
| `from_bytes_until_nul` | `library/core/src/ffi/c_str.rs` | `—` | `—` | safe method | `not started` | `UNKNOWN` | No dedicated proof harness yet. |
| `from_bytes_with_nul` | `library/core/src/ffi/c_str.rs` | `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs` and `kmir/cstr.smir.json` | `test_clone_to_uninit_exact_bytes` / `test_clone_to_uninit` | safe method | `blocked` | `MIR_SEMANTICS` | Both existing proof paths converge on the shared `core::ffi::CStr::from_bytes_with_nul` constructor/body frontier. |
| `count_bytes` | `library/core/src/ffi/c_str.rs` | `—` | `—` | safe method | `not started` | `UNKNOWN` | No dedicated proof harness yet. |
| `is_empty` | `library/core/src/ffi/c_str.rs` | `—` | `—` | safe method | `not started` | `UNKNOWN` | No dedicated proof harness yet. |
| `to_bytes` | `library/core/src/ffi/c_str.rs` | `—` | `—` | safe method | `not started` | `UNKNOWN` | No dedicated proof harness yet. |
| `to_bytes_with_nul` | `library/core/src/ffi/c_str.rs` | `—` | `—` | safe method | `not started` | `UNKNOWN` | No dedicated proof harness yet. |
| `bytes` | `library/core/src/ffi/c_str.rs` | `—` | `—` | safe method | `not started` | `UNKNOWN` | No dedicated proof harness yet. |
| `to_str` | `library/core/src/ffi/c_str.rs` | `—` | `—` | safe method | `not started` | `UNKNOWN` | No dedicated proof harness yet. |
| `as_ptr` | `library/core/src/ffi/c_str.rs` | `—` | `—` | safe method | `not started` | `UNKNOWN` | No dedicated proof harness yet. |
| `from_ptr` | `library/core/src/ffi/c_str.rs` | `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_ptr.rs` | `test_from_ptr` | unsafe item | `frontier reached` | `MIR_SEMANTICS` | Proof reaches a concrete failing frontier and is still under the branch-local blocker family. |
| `from_bytes_with_nul_unchecked` | `library/core/src/ffi/c_str.rs` | `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_bytes_with_nul_unchecked.rs` | `test_from_bytes_with_nul_unchecked_ok` | unsafe item | `frontier reached` | `MIR_SEMANTICS` | The proof now reaches a concrete thunk frontier inside the constructor path. |
| `strlen` | `library/core/src/ffi/c_str.rs` | `—` | `—` | unsafe item | `not started` | `UNKNOWN` | No dedicated `strlen` slice has been added yet. |
| `CloneToUninit` | `std::clone::CloneToUninit for CStr` | `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs` and `kmir/cstr.smir.json` | `test_clone_to_uninit_exact_bytes` / `test_clone_to_uninit` | trait impl | `blocked` | `MIR_SEMANTICS` | Exact-byte harness exists, but both proof paths currently stop at the shared `CStr::from_bytes_with_nul` body frontier and the donor-link root-name blocker. |
| `Index<RangeFrom<usize>>` | `core::ops::Index<RangeFrom<usize>> for CStr` | `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_ptr.rs` | `test_index_range_from_exact_bytes` | trait impl | `frontier reached` | `MIR_SEMANTICS` | The tail-preservation slice is present and still fails at a concrete frontier. |

