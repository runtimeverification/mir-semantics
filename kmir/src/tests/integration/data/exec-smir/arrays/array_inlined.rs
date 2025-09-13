const I8_ARRAY: [i8; 3] = [1, -2, 3];
const I32_ARRAY: [i32; 4] = [10, -20, 30, -40];

fn main() {
    
    // Product of first two elements
    let i8_product = I8_ARRAY[0] * I8_ARRAY[1];
    let i32_product = I32_ARRAY[0] * I32_ARRAY[1];
    
    // Assertions

    // these constants get allocated, which is not supported yet
    // assert_eq!(i8_product, -2); // 1 * (-2) = -2
    // assert_eq!(i32_product, -200); // 10 * -20 = -200

    // therefore using a computation instead of constants
    assert_eq!(i8_product as i32 * 100, i32_product);
}