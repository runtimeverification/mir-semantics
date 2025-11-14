struct Wrapper(u32);

fn roundtrip(ptr: *const Wrapper) -> u32 {
    unsafe {
        let erased = ptr as *const ();
        let restored = erased as *const Wrapper;
        (*restored).0
    }
}

fn main() {
    let value = Wrapper(0xCAFE_BABE);
    assert!(roundtrip(&value) == 0xCAFE_BABE);
}
