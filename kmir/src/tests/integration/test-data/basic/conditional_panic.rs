fn main() {
    let a = 1;
    let b = 2;
    let c = 3;
    let d:usize;

    if a + b == c {
        d = a;
    } else {
        d = b;
    }

    if d != a {
        panic!();
    }
}