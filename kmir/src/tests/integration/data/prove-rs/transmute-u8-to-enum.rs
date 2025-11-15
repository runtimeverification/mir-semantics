#[repr(u8)]
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum AccountState {
    Uninitialized,
    Initialized,
    Frozen,
}

fn main() {
    unsafe {
        assert_eq!(core::mem::transmute::<u8, AccountState>(0), AccountState::Uninitialized);
        assert_eq!(core::mem::transmute::<u8, AccountState>(1), AccountState::Initialized);
        assert_eq!(core::mem::transmute::<u8, AccountState>(2), AccountState::Frozen);
    }
}
