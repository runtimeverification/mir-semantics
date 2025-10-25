pub struct Point {
    x: i32,
    y: i32,
}

pub enum Foo {
    Bar,
    Baz(Point),
    Qux(u8, Option<u8>),
}

pub fn test(foo: Foo, bs: [u8; 8]) {
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
    let mut sum: u64 = 0;
    for b in bs {
        let b64 = u64::from(b);
        sum += b64;
        assert!(sum >= b64);
    }
}
