fn main() {
    // Shl basic
    assert!(1_u8 << 3_u8 == 8);
    assert!(1_u8 << 3_i8 == 8); // Negative on RHS if in 0..size
    assert!(1_i8 << 3_u8 == 8);
    assert!(1_i8 << 3_i8 == 8);
    assert!(1_i8 << 7_u8 == -128_i8);

    // Shl Overflow
    assert!(255_u8 << 1_u8 == 254);   
    assert!(-127_i8 << 1_u8 == 2);   
    // assert!(-128_i8 << -1_i8 == 2); // Shift must be in 0..size   
    // assert!(0_u8 << 8_u8 == 0);     // Shift must be in 0..size   

    // Shr basic
    assert!(24_u8 >> 3_u8 == 3);
    assert!(24_u8 >> 3_i8 == 3); // Negative on RHS if in 0..size
    assert!(24_i8 >> 3_u8 == 3);
    assert!(24_i8 >> 3_i8 == 3);

    // Shr Overflow
    assert!(255_u8 >> 1_u8 == 127);   
    assert!(-127_i8 >> 1_u8 == -64);   // Arithmetic shift sign extends   
    // assert!(-128_i8 >> -1_i8 == 2); // Shift must be in 0..size   
    // assert!(0_u8 >> 8_u8 == 0);     // Shift must be in 0..size   

    // ShlUnchecked basic
    assert!(1_u8.wrapping_shl(3_u32) == 8_u8); // RHS must be u32

    // ShlUnchecked Overflow
    assert!(255_u8.wrapping_shl(1_u32) == 254_u8);
    assert!(128_u8.wrapping_shl(1_u32) == 0_u8);
    assert!((-128_i8).wrapping_shl(3_u32) == 0_i8);
    assert!((-127_i8).wrapping_shl(3_u32) == 8_i8);

    // ShrUnchecked basic
    assert!(32_u8.wrapping_shr(2_u32) == 8_u8); // RHS must be u32

    // ShlUnchecked Overflow
    assert!(255_u8.wrapping_shr(1_u32) == 127_u8);
    assert!(128_u8.wrapping_shr(1_u32) == 64_u8);
    assert!((-128_i8).wrapping_shr(3_u32) == -16_i8);
    assert!((-127_i8).wrapping_shr(1_u32) == -64_i8);
}