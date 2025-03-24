fn main() {
    let mut x = 42i8;

    f(&mut x);
  
    assert!(x == 32);

    let xref = &mut x;

    *xref = 22;

    assert!(x == 22);
}

fn f(y: &mut i8) {
    *y = 32
}
