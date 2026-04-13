#[repr(C)]
struct KnownLayout {
    head: u8,
    tail: u32,
}

fn main() {
    assert!(core::mem::offset_of!(KnownLayout, tail) == 4);
}
