#[derive(Debug, PartialEq)]
enum SmallInt {
    One = 1,
    Two = 2,
}

fn foo(x: u8) -> Option<SmallInt> {
    match x {
        1 => Some(SmallInt::One),
        2 => Some(SmallInt::Two),
        _ => None,
    }
}

fn main() {
    assert_eq!(foo(0), None);
    assert_eq!(foo(1), Some(SmallInt::One));
    assert_eq!(foo(2), Some(SmallInt::Two));
}
