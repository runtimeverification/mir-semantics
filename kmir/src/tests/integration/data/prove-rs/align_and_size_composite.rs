use std::mem::{size_of, align_of};

fn main() {

    // Arrays
    assert_eq!(size_of::<[u8; 0]>(), 0);
    assert_eq!(align_of::<[u8; 0]>(), 1);

    assert_eq!(size_of::<[u8; 4]>(), 4);
    assert_eq!(align_of::<[u8; 4]>(), 1);

    assert_eq!(size_of::<[u64; 3]>(), 24);
    assert_eq!(align_of::<[u64; 3]>(), 8);

    // Tuples
    assert_eq!(size_of::<()>(), 0);
    assert_eq!(align_of::<()>(), 1);

    assert_eq!(size_of::<(u8, u16)>(), 4);
    assert_eq!(align_of::<(u8, u16)>(), 2);

    assert_eq!(size_of::<(u8, u64)>(), 16);
    assert_eq!(align_of::<(u8, u64)>(), 8);

    assert_eq!(size_of::<(u64, u8, u64)>(), 24);
    assert_eq!(align_of::<(u64, u8, u64)>(), 8);

    // rustc will permute fields (less padding)
    #[allow(dead_code)]
    struct Padded {
        a: u8,
        b: u64,
        c: u8,
    }
    assert_eq!(size_of::<Padded>(), 16);
    assert_eq!(align_of::<Padded>(), 8);

    // cannot permute fields
    #[allow(dead_code)]
    #[repr(C)]
    struct ReprC {
        a: u8,
        b: u64,
        c: u8,
    }
    assert_eq!(size_of::<ReprC>(), 24);
    assert_eq!(align_of::<ReprC>(), 8);

    #[allow(dead_code)]
    #[repr(packed)]
    struct ReprPacked {
        a: u8,
        b: u64,
        c: u8,
    }
    assert_eq!(size_of::<ReprPacked>(), 10);
    assert_eq!(align_of::<ReprPacked>(), 1);

    #[allow(dead_code)]
    struct SmallStruct {
        a: u8,
        b: u8,
        c: u8,
    }
    assert_eq!(size_of::<SmallStruct>(), 3);
    assert_eq!(align_of::<SmallStruct>(), 1);

    #[allow(dead_code)]
    struct AlignedStruct {
        a: u32,
        b: u32,
    }
    assert_eq!(size_of::<AlignedStruct>(), 8);
    assert_eq!(align_of::<AlignedStruct>(), 4);

    #[allow(dead_code)]
    #[repr(align(16))]
    struct Align16 {
        a: u8,
    }
    assert_eq!(size_of::<Align16>(), 16);
    assert_eq!(align_of::<Align16>(), 16);

    // Enums
    #[allow(dead_code)]
    enum SimpleEnum {
        A,
        B,
        C,
    }
    assert_eq!(size_of::<SimpleEnum>(), 1);
    assert_eq!(align_of::<SimpleEnum>(), 1);

    #[allow(dead_code)]
    enum EnumWithData {
        Variant1(u32),
        Variant2(u64),
    }
    assert_eq!(size_of::<EnumWithData>(), 16);
    assert_eq!(align_of::<EnumWithData>(), 8);

    #[allow(dead_code)]
    enum ComplexEnum {
        Small(u8),
        Medium(u32),
        Large(u64, u64),
    }
    assert_eq!(size_of::<ComplexEnum>(), 24);
    assert_eq!(align_of::<ComplexEnum>(), 8);

    // Option optimization
    assert_eq!(size_of::<Option<u32>>(), 8);
    assert_eq!(align_of::<Option<u32>>(), 4);

    // Null pointer optimization
    assert_eq!(size_of::<Option<&u32>>(), 8);
    assert_eq!(align_of::<Option<&u32>>(), 8);

    // Result
    assert_eq!(size_of::<Result<u32, u32>>(), 8);
    assert_eq!(align_of::<Result<u32, u32>>(), 4);

    assert_eq!(size_of::<Result<u64, u8>>(), 16);
    assert_eq!(align_of::<Result<u64, u8>>(), 8);

    // Zero-sized types
    struct ZeroSized;
    assert_eq!(size_of::<ZeroSized>(), 0);
    assert_eq!(align_of::<ZeroSized>(), 1);

}
