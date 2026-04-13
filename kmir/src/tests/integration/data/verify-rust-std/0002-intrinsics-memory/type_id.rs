use std::any::TypeId;

fn main() {
    assert!(TypeId::of::<i32>() == TypeId::of::<i32>());
}
