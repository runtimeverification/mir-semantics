fn test(x: usize, y:usize) -> bool {
    return x > y;
}


fn main() {
  let x:usize = 42;
  let y:usize = 0;
  let z:bool = test(x, y);
  assert!(z);
  return ();
}
