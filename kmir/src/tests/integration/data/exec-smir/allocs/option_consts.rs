const OPT_NO_U32: Option<u32> = None;
const OPT_A_U64:  Option<u64> = Some(42);
const OPT_NO_REF: Option<&[u32;3]> = None;

fn main() {
    let a = 1;
    let result = sub_(0,a);
    assert_eq!(result, OPT_NO_U32);
    assert_eq!(OPT_A_U64, Some(41 + a as u64));
    assert!(OPT_NO_REF.is_none());
    let arr0 = [0u32; 3];
    assert_eq!(opt_ref(&arr0), None);
    let arr = [a;3];
    assert_eq!(opt_ref(&arr), Some(&arr));
}

// basically checked_sub
fn sub_(a:u32, b:u32) -> Option<u32> {
    if a < b {
        None  // this becomes an Operand::Constant
    } else {
        Some(a - b)
    }
}

fn opt_ref(arr: &[u32;3]) -> Option<&[u32;3]> {
    if arr[0] == 0 {
        None
    } else {
        Some(arr)
    }
}