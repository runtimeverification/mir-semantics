fn main() {
    let arr = [11, 22, 33];
    let mid_ref = unsafe { arr.get_unchecked(1) };
    let mid = *mid_ref;
    assert!(mid == 22);
    let last = unsafe { arr.get_unchecked(2) };
    assert!(*last == 33);
}