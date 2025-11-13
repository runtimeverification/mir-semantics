use std::convert::TryFrom;

pub enum ProgramError {
    InvalidAccountData
}

#[repr(u8)]
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum AccountState {
    Uninitialized,
    Initialized,
    Frozen,
}

impl TryFrom<u8> for AccountState {
    type Error = ProgramError;

    #[inline(always)]
    fn try_from(value: u8) -> Result<Self, Self::Error> {
        match value {
            // SAFETY: `value` is guaranteed to be in the range of the enum variants.
            0..=2 => Ok(unsafe { core::mem::transmute::<u8, AccountState>(value) }),
            _ => Err(ProgramError::InvalidAccountData),
        }
    }
}

fn main() {
    num_into_state(0);
}

fn num_into_state(arg: u8) {
    let state: Result<AccountState, ProgramError> = AccountState::try_from(arg);

    if arg <= 2 {
        assert!(state.is_ok());
    } else {
        assert!(state.is_err());
    }
}