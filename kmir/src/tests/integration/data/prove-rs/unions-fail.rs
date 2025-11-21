union Union {
    signed: i8,
    unsigned: u8,
}

fn main() {
    let s = Union { signed: -1 };
    let u = Union { unsigned: 255 };
    unsafe {
        assert!(s.signed == -1);
        assert!(s.unsigned == 255);

        assert!(u.signed == -1);
        assert!(u.unsigned == 255);
    }
}
