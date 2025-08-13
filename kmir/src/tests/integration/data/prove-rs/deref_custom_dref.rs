use std::ops::Deref;

struct Wrapper(i32); // Not Copy (no derive)

impl Deref for Wrapper {
    type Target = i32;
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

fn main() {
    let w = Wrapper(42);
    // Uses Deref (not CopyForDeref)
    assert!(*w == 42);
}