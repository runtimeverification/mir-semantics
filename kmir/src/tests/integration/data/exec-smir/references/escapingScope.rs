fn main() {
    let x = 42i8;

    unsafe {
        let z = f(&x);
        assert!(*z == x);
    }
}

unsafe fn f(_:&i8) -> &i8{
    let x = 42;
    unsafe {
        let y = &x;
        // does not compile! (good)
        return y;
    }
}