fn main() {
    let arr = [1, 2, 3];
    let _x: i32;
    unsafe {
        let p = arr.as_ptr().add(3);
        _x = *p; // <-- UB
    }
}
