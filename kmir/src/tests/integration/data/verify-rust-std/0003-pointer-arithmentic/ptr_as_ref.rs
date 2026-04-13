fn main() {
    let value = 42i32;
    let value_ref = &value;
    let ptr = value_ref as *const i32;
    let maybe_ref = unsafe { ptr.as_ref() };

    match maybe_ref {
        Some(raw_ref) => assert!(*raw_ref == 42),
        None => assert!(false),
    }
}
