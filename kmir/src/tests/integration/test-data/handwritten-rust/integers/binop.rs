fn test_binop(x:i32, y:i32) -> () {
// Arithmetic
    // Addition
    assert!(x + y == 52);
    assert!(52 == x + y);
    assert!(x + y == y + x);

    // Subtraction
    assert!(x - y == 32);
    assert!(y - x == -32);
    assert!(y - x != x - y);

    // Multiplication
    assert!(x * y == 420);
    assert!(x * -y == -420);
    assert!(-x * y == -420);
    assert!(-x * -y == 420);

    // Division
    // assert!(420 / 10 == 42); // FAILING SEE div.rs and div.mir
    
    // Modulo
    // assert!(x % 10 == 2); // FAILING SEE modulo.rs and modulo.mir

// Bitwise
    // Xor
    assert!(1 ^ 2 == 3);
    assert!(1 ^ 3 == 2);

    // Or
    assert!(1 | 2 == 3);
    assert!(1 | 3 == 3);

    // And
    assert!(1 & 2 == 0);
    assert!(1 & 3 == 1);

    // // Shl
    assert!(2 << 1 == 4);
    // assert!(-128_i8 << 1 == 0); FAILS SEE shl_min.rs and shl_min.mir
    // assert!(-32768_i16 << 1 == 0); FAILS SEE shl_min.rs and shl_min.mir
    // assert!(-2147483648_i32 << 1 == 0); FAILS SEE shl_min.rs and shl_min.mir
    // assert!(-9223372036854775808_i64 << 1 == 0); FAILS SEE shl_min.rs and shl_min.mir
    // assert!(-17014118346046923173168730371588410572_i128 << 1 == 0); FAILS SEE shl_min.rs and shl_min.mir


    // // Shr
    assert!(2 >> 1 == 1);
    assert!(3 >> 1 == 1);
    assert!(1 >> 1 == 0);

// Comparisions
    // Less Then
    assert!(x < x + y);

    // Less Then or Equal
    assert!(x <= x + y);
    assert!(x <= x + y - y);

    // Greater Then
    assert!(x + y > x);

    // Greater Then or Equal 
    assert!(x + y >= x);
    assert!(x + y - y >= x);
}


fn main() {
  let x = 42;
  let y = 10;
  test_binop(x, y);
  return ();
}
