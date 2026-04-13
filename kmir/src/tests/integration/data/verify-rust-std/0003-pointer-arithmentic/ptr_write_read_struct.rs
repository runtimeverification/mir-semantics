#[derive(Copy, Clone)]
struct Pair {
    a: i32,
    b: u8,
}

fn main() {
    let mut pair = Pair { a: 1, b: 2 };
    let pair_ptr = &mut pair as *mut Pair;

    let read_back: Pair;
    unsafe {
        core::ptr::write(pair_ptr, Pair { a: 123, b: 9 });
        read_back = core::ptr::read(pair_ptr as *const Pair);
    }

    assert!(read_back.a == 123);
    assert!(read_back.b == 9);
    assert!(pair.a == 123);
    assert!(pair.b == 9);
}
