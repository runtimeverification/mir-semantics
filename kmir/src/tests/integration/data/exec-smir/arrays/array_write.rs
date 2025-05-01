fn main() {

    let mut a: [i16; 4] = [1;4];

    a[0] = 2;

    let b = &mut (a[1]);

    *b = 2;

    assert!(a[0] == a[1]);
}
