use std::ffi::{c_char, CStr};

macro_rules! precondition {
    ($cond:expr, $body:block) => {
        if $cond $body
    };
}

fn main() {
    test_from_ptr();
    test_index_range_from_exact_bytes(0);
}

fn test_from_ptr() {
    let bytes: [u8; 6] = [b'h', b'e', b'l', b'l', b'o', 0];
    let ptr = bytes.as_ptr() as *const c_char;

    precondition!(!ptr.is_null(), {
        let cstr = unsafe { CStr::from_ptr(ptr) };
        let as_bytes = cstr.to_bytes();
        assert!(as_bytes.len() == 5);
        assert!(as_bytes[0] == b'h');
        assert!(as_bytes[4] == b'o');
    });
}

fn test_index_range_from_exact_bytes(start: usize) {
    let cstr = CStr::from_bytes_with_nul(b"hello\0");
    match cstr {
        Ok(s) => {
            precondition!(start <= 5, {
                let tail = &s[start..];
                let b = tail.to_bytes();
                assert!(b.len() == 5 - start);
                if start == 0 {
                    assert!(b[0] == b'h');
                    assert!(b[4] == b'o');
                } else if start == 1 {
                    assert!(b[0] == b'e');
                    assert!(b[3] == b'o');
                } else if start == 2 {
                    assert!(b[0] == b'l');
                    assert!(b[2] == b'o');
                } else if start == 3 {
                    assert!(b[0] == b'l');
                    assert!(b[1] == b'o');
                } else if start == 4 {
                    assert!(b[0] == b'o');
                }
            });
        }
        Err(_) => panic!("expected Ok"),
    }
}
