// ptr-cast-elem-offset-fail.rs
fn main() {
    let arr: [i32; 2] = [42, 84];
    let r_arr = &arr;
    let p_arr = r_arr as *const i32;
    
    unsafe {
        let p_arr_offset = p_arr.offset(1);
        assert!(*p_arr_offset == 84);
    }
}
