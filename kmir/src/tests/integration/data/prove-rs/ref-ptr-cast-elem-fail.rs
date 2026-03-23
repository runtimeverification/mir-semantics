fn main() {
    let arr: [i32; 1] = [42];
    let r_arr = &arr;
    let p_arr = r_arr as *const i32;
    
    unsafe {
        assert!(*p_arr == 42);
    }
}
