#[repr(u8)]
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum AccountState {
    Uninitialized = 11,
    Initialized = 22,
    Frozen = 255,
}

fn main() {
    unsafe {
        assert_eq!(core::mem::transmute::<u8, AccountState>(11), AccountState::Uninitialized);
        assert_eq!(core::mem::transmute::<u8, AccountState>(22), AccountState::Initialized);
        assert_eq!(core::mem::transmute::<u8, AccountState>(255), AccountState::Frozen);

        // Compiler rejects transmuting between different width types
        // assert_eq!(core::mem::transmute::<u64, AccountState>(-1), AccountState::Frozen);

        // The within the same width the type can be different, here an `-1_i8` is used instead
        // of a `255_u8`, but the bit pattern matches it creates the correct type
        assert_eq!(core::mem::transmute::<i8, AccountState>(-1), AccountState::Frozen);
    }
}
