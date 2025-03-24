fn main() {
    let x = 42i8;

    let z = f(&x);

    assert!(z == x);
}

fn f(y: &i8) -> i8{
    *y
}
