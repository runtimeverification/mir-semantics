use std::mem::{size_of, align_of};


fn check_size_and_alignment<T>(size: usize, align: usize){
    let s = size_of::<T>();
    let a = align_of::<T>();

    assert_eq!(s, size);
    assert_eq!(a, align);
}


fn main() {
    // // Basic integer types
    check_size_and_alignment::<u8>(1, 1);
    check_size_and_alignment::<u32>(4, 4);

    check_size_and_alignment::<u8>(1, 1);
    
    check_size_and_alignment::<i8>(1, 1);
    
    check_size_and_alignment::<u16>(2, 2);
    
    check_size_and_alignment::<i16>(2, 2);
    
    check_size_and_alignment::<u32>(4, 4);
    
    check_size_and_alignment::<i32>(4, 4);
    
    check_size_and_alignment::<u64>(8, 8);
    
    check_size_and_alignment::<i64>(8, 8);
    
    check_size_and_alignment::<u128>(16, 16);
    
    check_size_and_alignment::<i128>(16, 16);
    
    // // Floating point types
    check_size_and_alignment::<f32>(4, 4);
    
    check_size_and_alignment::<f64>(8, 8);
    
    // // Other basic types
    check_size_and_alignment::<bool>(1, 1);
    
    check_size_and_alignment::<char>(4, 4);
    
    // // Pointer-sized types (64-bit)
    check_size_and_alignment::<usize>(8, 8);
    
    check_size_and_alignment::<isize>(8, 8);
    
    check_size_and_alignment::<&u32>(8, 8);
    
    check_size_and_alignment::<*const u32>(8, 8);
    
    check_size_and_alignment::<*mut u32>(8, 8);
    
    // Fat pointers (2x pointer size on 64-bit)
    check_size_and_alignment::<&[u32]>(16, 8);
    
    // check_size_and_alignment::<&str>(16, 8);
    
    check_size_and_alignment::<&mut [u32]>(16, 8);
    
    // // Arrays
    check_size_and_alignment::<[u8; 0]>(0, 1);
    
    check_size_and_alignment::<[u8; 4]>(4, 1);
    
    check_size_and_alignment::<[u8; 16]>(16, 1);
    
    check_size_and_alignment::<[u32; 4]>(16, 4);
    
    check_size_and_alignment::<[u64; 3]>(24, 8);
    
    // // Tuples
    check_size_and_alignment::<()>(0, 1);
    
    check_size_and_alignment::<(u8,)>(1, 1);
    
    check_size_and_alignment::<(u8, u8)>(2, 1);
    
    check_size_and_alignment::<(u8, u16)>(4, 2);
    
    check_size_and_alignment::<(u8, u32)>(8, 4);
    
    check_size_and_alignment::<(u8, u64)>(16, 8);
    
    check_size_and_alignment::<(u32, u32)>(8, 4);
    
    check_size_and_alignment::<(u64, u8, u64)>(24, 8);
    
    // rustc will permute fields (less padding)
    #[allow(dead_code)]
    struct Padded {
        a: u8,
        b: u64,
        c: u8,
    }
    check_size_and_alignment::<Padded>(16, 8);
    
    // cannot permute fields
    #[allow(dead_code)]
    #[repr(C)]
    struct ReprC {
        a: u8,
        b: u64,
        c: u8,
    }
    check_size_and_alignment::<ReprC>(24, 8);
    
    #[allow(dead_code)]
    #[repr(packed)]
    struct ReprPacked {
        a: u8,
        b: u64,
        c: u8,
    }
    check_size_and_alignment::<ReprPacked>(10, 1);
    
    #[allow(dead_code)]
    struct SmallStruct {
        a: u8,
        b: u8,
        c: u8,
    }
    check_size_and_alignment::<SmallStruct>(3, 1);
    
    #[allow(dead_code)]
    struct AlignedStruct {
        a: u32,
        b: u32,
    }
    check_size_and_alignment::<AlignedStruct>(8, 4);
    
    #[allow(dead_code)]
    #[repr(align(16))]
    struct Align16 {
        a: u8,
    }
    check_size_and_alignment::<Align16>(16, 16);
    
    #[allow(dead_code)]
    #[repr(align(32))]
    struct Align32 {
        a: u32,
    }
    check_size_and_alignment::<Align32>(32, 32);
    
    // Enums
    #[allow(dead_code)]
    enum SimpleEnum {
        A,
        B,
        C,
    }
    check_size_and_alignment::<SimpleEnum>(1, 1);
    
    #[allow(dead_code)]
    enum EnumWithData {
        Variant1(u32),
        Variant2(u64),
    }
    check_size_and_alignment::<EnumWithData>(16, 8);
    
    #[allow(dead_code)]
    enum ComplexEnum {
        Small(u8),
        Medium(u32),
        Large(u64, u64),
    }
    check_size_and_alignment::<ComplexEnum>(24, 8);
    
    // // Option optimization
    check_size_and_alignment::<Option<u32>>(8, 4);
    
    check_size_and_alignment::<Option<u64>>(16, 8);
    
    // Null pointer optimization
    check_size_and_alignment::<Option<&u32>>(8, 8);
    
    check_size_and_alignment::<Option<Box<u32>>>(8, 8);
    
    // Result
    check_size_and_alignment::<Result<u32, u32>>(8, 4);
    
    check_size_and_alignment::<Result<u64, u8>>(16, 8);
    
    // Zero-sized types
    struct ZeroSized;
    check_size_and_alignment::<ZeroSized>(0, 1);
    
    struct PhantomStruct<T> {
        _marker: std::marker::PhantomData<T>,
    }
    check_size_and_alignment::<PhantomStruct<u64>>(0, 1);
    
    // // String and Vec (heap-allocated)
    check_size_and_alignment::<String>(24, 8);
    
    check_size_and_alignment::<Vec<u32>>(24, 8);
    
    check_size_and_alignment::<Box<u32>>(8, 8);
    
    check_size_and_alignment::<Box<[u32]>>(16, 8);

}