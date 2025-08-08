fn main() {
    let a = [1,2,3u8];
    f(&a);
    let a = [4,5,6,7,8,9u8];
    f(&a);
}

fn f(xs: &[u8]) {
    // let [a, b, c, rest @ ..] = xs
    // else { panic!("Need at least three elements"); };
    // println!("Array {xs:?} is ( {a}, {b}, {c}, {rest:?} )");

    if let [a, b, c, rest @ ..] = xs {
        assert!(a + b - c == rest.len() as u8);
    }
}
