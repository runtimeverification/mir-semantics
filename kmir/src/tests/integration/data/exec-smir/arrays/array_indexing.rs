fn main() {

    let a: [i16; 4] = [1;4];

    let b = a[0];
    let c = a[b as usize];

    assert!(b == c);
}
