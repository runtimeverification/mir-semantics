#[repr(packed)]
struct Packed {
    prefix: u8,
    value: u32,
}

fn main() {
    let packed = Packed {
        prefix: 1,
        value: 0x11223344,
    };
    let value_ptr = core::ptr::addr_of!(packed.value);

    let copied: u32;
    unsafe {
        copied = core::ptr::read_unaligned(value_ptr);
    }

    assert!(copied == 0x11223344);
}
