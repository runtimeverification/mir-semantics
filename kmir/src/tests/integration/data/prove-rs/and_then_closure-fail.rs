use std::result::Result;

fn wrap(x: &u32) -> Result<&u32, u8> { Ok(x) }

fn main() {
    let single: u32 = 32;

    let wrapped: Result<u32, u8> = wrap(&single).and_then(|x: &u32| if *x <= 42 {Ok(42)} else {Err(43)});

    assert_eq!(wrapped, Ok(42));
}
