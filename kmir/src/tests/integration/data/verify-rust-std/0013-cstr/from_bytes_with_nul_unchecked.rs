use std::ffi::CStr;

fn main() {
    test_from_bytes_with_nul_unchecked_ok();
}

fn test_from_bytes_with_nul_unchecked_ok() {
    let bytes: &[u8] = b"rust\0";
    let cstr = unsafe { CStr::from_bytes_with_nul_unchecked(bytes) };
    let view = cstr.to_bytes();

    assert!(view.len() == 4);
    assert!(view[0] == b'r');
    assert!(view[1] == b'u');
    assert!(view[2] == b's');
    assert!(view[3] == b't');
}
