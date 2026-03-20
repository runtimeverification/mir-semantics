struct Wrapper(u64);

fn main() {
    let val: u64 = 42;
    let wrapped: Wrapper = unsafe { core::mem::transmute::<u64, Wrapper>(val) };
    assert!(wrapped.0 == 42);
}
