fn main() {
    let mut data = 11;
    let ptr = &data as *const i32;

    let ptr_mut = &mut data as *mut i32;
    unsafe {
        (*ptr_mut) = 44;
        assert_eq!(44, *ptr); // FIXME: fails due to thunks on casts
    }
}
