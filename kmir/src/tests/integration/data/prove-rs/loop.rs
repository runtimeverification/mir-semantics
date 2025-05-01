fn property_test() {
    let mut x = 0;
    let y = 10;
    let mut s = 0;

    while x < y {
        x += 1;
        s += x;
    }

    assert!(s == 55);

}

fn main() {
    property_test();
}