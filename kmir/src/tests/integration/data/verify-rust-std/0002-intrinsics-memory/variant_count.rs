#![feature(variant_count)]

fn main() {
    assert!(core::mem::variant_count::<Option<i32>>() == 2);
}
