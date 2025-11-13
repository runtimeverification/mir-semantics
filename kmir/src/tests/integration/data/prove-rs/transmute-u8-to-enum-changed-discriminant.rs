#[repr(u8)]
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum AccountState {
    Uninitialized = 11,
    Initialized = 22,
    Frozen = 33,
}

fn main() {
    unsafe {
        assert_eq!(core::mem::transmute::<u8, AccountState>(11), AccountState::Uninitialized);
        assert_eq!(core::mem::transmute::<u8, AccountState>(22), AccountState::Initialized);
        assert_eq!(core::mem::transmute::<u8, AccountState>(33), AccountState::Frozen);
    }
}
