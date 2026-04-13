fn main() {
    let src = [1u8, 2u8, 3u8, 4u8];
    let mut dst = [0u8, 0u8, 0u8, 0u8];

    unsafe {
        core::ptr::copy_nonoverlapping(src.as_ptr(), dst.as_mut_ptr(), src.len());
    }

    assert!(dst == src);
}
