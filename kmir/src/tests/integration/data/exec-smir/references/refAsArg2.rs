// references across several function calls
fn main() {
    let x = 42i8;

    let z = f(&x);

    assert!(z == x);
}

// returning references (back, not from locals)
fn f(x:&i8) -> i8 {
    g(x)
}
fn g(x:&i8) -> i8 {
    *x
}
