use std::mem::{size_of, align_of};

fn main() {
    // Basic integer types
    assert_eq!(size_of::<u8>(), 1);
    assert_eq!(align_of::<u8>(), 1);

    assert_eq!(size_of::<i8>(), 1);
    assert_eq!(align_of::<i8>(), 1);

    assert_eq!(size_of::<u16>(), 2);
    assert_eq!(align_of::<u16>(), 2);

    assert_eq!(size_of::<i16>(), 2);
    assert_eq!(align_of::<i16>(), 2);

    assert_eq!(size_of::<u32>(), 4);
    assert_eq!(align_of::<u32>(), 4);

    assert_eq!(size_of::<i32>(), 4);
    assert_eq!(align_of::<i32>(), 4);

    assert_eq!(size_of::<u64>(), 8);
    assert_eq!(align_of::<u64>(), 8);

    assert_eq!(size_of::<i64>(), 8);
    assert_eq!(align_of::<i64>(), 8);

    assert_eq!(size_of::<u128>(), 16);
    assert_eq!(align_of::<u128>(), 16);

    assert_eq!(size_of::<i128>(), 16);
    assert_eq!(align_of::<i128>(), 16);

    // Floating point types
    assert_eq!(size_of::<f32>(), 4);
    assert_eq!(align_of::<f32>(), 4);

    assert_eq!(size_of::<f64>(), 8);
    assert_eq!(align_of::<f64>(), 8);

    // Other basic types
    assert_eq!(size_of::<bool>(), 1);
    assert_eq!(align_of::<bool>(), 1);

    assert_eq!(size_of::<char>(), 4);
    assert_eq!(align_of::<char>(), 4);

    // Pointer-sized types (64-bit)
    assert_eq!(size_of::<usize>(), 8);
    assert_eq!(align_of::<usize>(), 8);

    assert_eq!(size_of::<isize>(), 8);
    assert_eq!(align_of::<isize>(), 8);

    assert_eq!(size_of::<&u32>(), 8);
    assert_eq!(align_of::<&u32>(), 8);

    assert_eq!(size_of::<*const u32>(), 8);
    assert_eq!(align_of::<*const u32>(), 8);

    assert_eq!(size_of::<*mut u32>(), 8);
    assert_eq!(align_of::<*mut u32>(), 8);
    // Fat pointers (2x pointer size on 64-bit)
    assert_eq!(size_of::<&[u32]>(), 16);
    assert_eq!(align_of::<&[u32]>(), 8);

    // assert_eq!(size_of::<&str>(), 16);
    // assert_eq!(align_of::<&str>(), 8);

    assert_eq!(size_of::<&mut [u32]>(), 16);
    assert_eq!(align_of::<&mut [u32]>(), 8);

}
