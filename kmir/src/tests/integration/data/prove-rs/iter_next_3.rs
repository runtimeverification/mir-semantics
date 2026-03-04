struct Wrapper {
    tag: u8,
    a: [[u8; 32]; 3],
}

fn foo(c: &Wrapper) {
    for elem in c.a.iter() {
        assert!(elem[0] != 0);
    }
}

fn main() {
    let c = Wrapper {
        tag: 42,
        a: [[1u8; 32], [2u8; 32], [3u8; 32]],
    };

    foo(&c);
}
