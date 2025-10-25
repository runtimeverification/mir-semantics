pub struct Point {
    x: i32,
    y: i32,
}

pub enum Foo {
    Bar,
    Baz(Point),
    Qux(u8, Option<u8>),
}

pub fn test(foo: Foo) {
    match foo {
        Foo::Bar => {},
        Foo::Baz(Point { x, y }) => if x >= y {
            assert!(x - y >= 0);
        } else {
            assert!(y - x >= 0);
        },
        Foo::Qux(x, Some(y)) => {
            assert!(u16::from(x) + u16::from(y) >= u16::from(x + y));
        },
        _ => {},
    }
}
