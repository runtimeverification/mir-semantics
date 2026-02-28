#[repr(i8)]
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum AccountState {
    Uninitialized = 0,
    Initialized = 1,
    Frozen = -1,
}

fn main() {
    unsafe {
        assert_eq!(core::mem::transmute::<u8, AccountState>(0), AccountState::Uninitialized);
        assert_eq!(core::mem::transmute::<i8, AccountState>(0), AccountState::Uninitialized);

        assert_eq!(core::mem::transmute::<u8, AccountState>(1), AccountState::Initialized);
        assert_eq!(core::mem::transmute::<i8, AccountState>(1), AccountState::Initialized);

        assert_eq!(core::mem::transmute::<u8, AccountState>(255), AccountState::Frozen);
        assert_eq!(core::mem::transmute::<i8, AccountState>(-1), AccountState::Frozen);
    }
}
