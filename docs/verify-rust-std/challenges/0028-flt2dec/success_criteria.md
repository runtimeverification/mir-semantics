# Success Criteria: Challenge 0028

Source basis:

- `model-checking/verify-rust-std` commit `7056130`
- `doc/src/challenges/0028-flt2dec.md`

| Function | Location | Status | Specification | Notes |
| --- | --- | --- | --- | --- |
| `digits_to_dec_str` | `core::num::flt2dec` | `partial` | Safe body of the decimal-digit formatter | Branch evidence exists only for the challenge-local `digits_to_dec_str_probe.rs` frontier; the exact copied `if exp >= buf.len()` select is still the current boundary. |
| `digits_to_exp_str` | `core::num::flt2dec` | `not started` | Safe body of the exponent-format formatter | No branch-local proof artifact yet. |
| `to_shortest_str` | `core::num::flt2dec` | `not started` | Safe body of the shortest-string formatter | No branch-local proof artifact yet. |
| `to_shortest_exp_str` | `core::num::flt2dec` | `not started` | Safe body of the shortest-exponent formatter | No branch-local proof artifact yet. |
| `to_exact_exp_str` | `core::num::flt2dec` | `not started` | Safe body of the exact-exponent formatter | No branch-local proof artifact yet. |
| `to_exact_fixed_str` | `core::num::flt2dec` | `not started` | Safe body of the exact-fixed formatter | No branch-local proof artifact yet. |
| `format_shortest_opt` | `core::num::flt2dec::grisu` | `not started` | Grisu wrapper for shortest formatting | No branch-local proof artifact yet. |
| `format_shortest` | `core::num::flt2dec::grisu` | `not started` | Grisu wrapper for shortest formatting | No branch-local proof artifact yet. |
| `format_exact_opt` | `core::num::flt2dec::dragon` | `not started` | Dragon wrapper for exact formatting | No branch-local proof artifact yet. |
| `format_exact` | `core::num::flt2dec::dragon` | `not started` | Dragon wrapper for exact formatting | No branch-local proof artifact yet. |
