struct Wrapper(u64);

fn main() {
    let wrapped = Wrapper(42);
    let val: u64 = unsafe { core::mem::transmute::<Wrapper, u64>(wrapped) };
    assert!(val == 42);
}
