use std::cell::UnsafeCell;
use std::mem::transmute;

fn main() {
    let cell = UnsafeCell::new(0_u8);
    let ptr = cell.get();

    // Model code that leaks a raw pointer address to user space.
    let leaked_addr = unsafe { transmute::<*mut u8, usize>(ptr) };

    // …and then turns the address back into a pointer, assuming round-trip soundness.
    let restored_ptr = unsafe { transmute::<usize, *mut u8>(leaked_addr) };

    // assert_eq!(ptr, restored_ptr);
}
