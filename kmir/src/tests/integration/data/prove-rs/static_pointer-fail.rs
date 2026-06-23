static NUM: u8 = 55;

fn main() {
    let num_ptr = &NUM as *const u8;
    unsafe {
        assert!(*num_ptr == 55);
    }
}
