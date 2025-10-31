#[repr(transparent)]
#[derive(Clone, Copy)]
struct Wrapper(u32);

fn main() {
    let w = Wrapper(13);
    let round_tripped = round_trip(&w);
    // If the cast alignment is wrong, dereferencing `round_tripped`
    // will read the inner `u32` instead of the whole `Wrapper`,
    // so destructuring as `Wrapper` fails.
    let Wrapper(v) = unsafe { *round_tripped };
    assert!(v == 13);
}

fn round_trip(wrapper: &Wrapper) -> *const Wrapper {
    unsafe {
        let p0: *const Wrapper = wrapper;
        let p1: *const u32 = p0 as *const u32;
        p1 as *const Wrapper
    }
}
