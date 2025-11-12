use std::mem::transmute;

fn main() {
    let mut byte = 0_u8;
    let ptr = &mut byte as *mut u8;

    // Leak the raw pointer address as an integer.
    let leaked_addr = unsafe { transmute::<*mut u8, usize>(ptr) };

    // Turn it back into a pointer, assuming round-trip soundness.
    let restored_ptr = unsafe { transmute::<usize, *mut u8>(leaked_addr) };

    assert_eq!(ptr, restored_ptr);
}
