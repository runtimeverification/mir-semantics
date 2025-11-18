#![feature(core_intrinsics)]
#![feature(never_type)]
use std::intrinsics::assert_inhabited;

fn main() {
    std::hint::black_box(
        assert_inhabited::<!>() // Up to compiler/CodegenBackend to panic or NOOP
    );
}
