#[repr(u8)]
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum AccountState {
    Uninitialized,
    Initialized,
    Frozen,
}

fn main() {
    unsafe {
        std::hint::black_box(
            core::mem::transmute::<u8, AccountState>(4)
        );
    }
}
