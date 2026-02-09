fn main() {
    let arr: [i32; 2] = [42, 84];
    let r_arr = &arr;
    let p_arr_wide = r_arr as *const [i32; 2];
    let p_arr_narrow = p_arr_wide as *const [i32; 1];
    
    unsafe {
        let p_arr_narrow_offset = p_arr_narrow.offset(1);
        assert!(*p_arr_narrow_offset == [84]);
    }
}
