#![feature(core_intrinsics)]

fn foo() {
    let x = std::hint::black_box(42);
    bar();
    assert!(x == 42);
}

fn bar() {
    std::intrinsics::assert_inhabited::<i32>();
}

fn main() {
    foo();
}
