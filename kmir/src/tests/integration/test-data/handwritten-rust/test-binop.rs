fn test_binop(x:usize, y:usize) -> () {
    assert!(x + y > x);
    assert!(x + y == 52);
    assert!(x + y == y + x);
    assert!(x + y == 52);
    assert!(x - y == 32);
    // TODO: add asserts for other binops
}


fn main() {
  let x = 42;
  let y = 10;
  test_binop(x, y);
  return ();
}
