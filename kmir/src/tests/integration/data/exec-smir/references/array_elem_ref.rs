// reference into array

fn f(x: &u32) {
  assert!(*x == 0);
}

fn g(x: *const u32) {
//   assert!(unsafe{*x} == 0); // deref alignment check currently failing
}

fn main() {
  let a = [0_u32; 4];
  let i = 3;
  let x = &a[i];
  let xx = x as *const u32;

  f(x);
  g(xx);
}

