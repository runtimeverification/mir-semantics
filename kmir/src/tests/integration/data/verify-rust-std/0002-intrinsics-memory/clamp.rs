fn main() {
    let clamped_high = 10_i32.clamp(0_i32, 5_i32);
    let clamped_mid = 3_i32.clamp(0_i32, 5_i32);

    assert!(clamped_high == 5_i32);
    assert!(clamped_mid == 3_i32);
}
