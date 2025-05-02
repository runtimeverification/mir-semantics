fn main () {
    let a:u32 = 4294967295;
    let b:u32 = 4294967294 + 1;
    assert!(a == b)
}