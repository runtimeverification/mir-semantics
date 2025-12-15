// Test case reproducing issues:
// - https://github.com/runtimeverification/mir-semantics/issues/891
// - https://github.com/runtimeverification/mir-semantics/issues/488
// - https://github.com/runtimeverification/stable-mir-json/issues/55
//
// Problem: Option::map with a function pointer (not a closure) causes
// "unknown function -1" error because function pointers passed as arguments
// are not included in the `functions` array in stable-mir-json output.
//
// Original example from issue #891:
//   .map(u64::from_le_bytes)  // fails - function pointer
//
// Workaround: use a closure instead:
//   .map(|bytes| u64::from_le_bytes(bytes))  // works

fn main() {
    let bytes: [u8; 8] = [0x15, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00];
    let opt: Option<[u8; 8]> = Some(bytes);

    // This fails: passing function pointer to Option::map
    // The MIR desugaring of Option::map invokes the function via a pointer,
    // but the function is not present in the `functions` array.
    let result = opt.map(u64::from_le_bytes);

    assert_eq!(result, Some(21u64));
}
