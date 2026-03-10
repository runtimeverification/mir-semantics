use std::cell::RefCell;
use std::convert::TryInto;
use std::rc::Rc;

type ProgramResult = Result<(), ProgramError>;

fn main() {
    let _keep: fn(&AccountInfo<'_>) -> ProgramResult = repro;
}

#[no_mangle]
pub fn repro(source_account_info: &AccountInfo<'_>) -> ProgramResult {
    cheatcode_is_spl_account(source_account_info);
    let account = get_account(source_account_info)?;

    if account.state == AccountState::Frozen {
        Err(ProgramError::Custom(7))
    } else {
        Ok(())
    }
}

#[inline(never)]
fn cheatcode_is_spl_account(_: &AccountInfo<'_>) {}

#[derive(Clone)]
struct AccountInfo<'a> {
    key: &'a Pubkey,
    lamports: Rc<RefCell<&'a mut u64>>,
    data: Rc<RefCell<&'a mut [u8]>>,
    owner: &'a Pubkey,
    rent_epoch: u64,
    is_signer: bool,
    is_writable: bool,
    executable: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Pubkey([u8; 32]);

impl Pubkey {
    fn new(bytes: [u8; 32]) -> Self {
        Self(bytes)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum ProgramError {
    InvalidAccountData,
    Custom(u32),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum AccountState {
    Uninitialized,
    Initialized,
    Frozen,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum COption<T> {
    None,
    Some(T),
}

#[derive(Clone, Copy, Debug)]
struct Account {
    mint: Pubkey,
    owner: Pubkey,
    amount: u64,
    delegate: COption<Pubkey>,
    state: AccountState,
    is_native: COption<u64>,
    delegated_amount: u64,
    close_authority: COption<Pubkey>,
}

impl Account {
    const LEN: usize = 165;

    fn unpack_from_slice(data: &[u8]) -> Result<Self, ProgramError> {
        if data.len() < Self::LEN {
            return Err(ProgramError::InvalidAccountData);
        }

        let mint = Pubkey::new(data[0..32].try_into().unwrap());
        let owner = Pubkey::new(data[32..64].try_into().unwrap());
        let amount = u64::from_le_bytes(data[64..72].try_into().unwrap());
        let state = match data[108] {
            0 => AccountState::Uninitialized,
            1 => AccountState::Initialized,
            2 => AccountState::Frozen,
            _ => return Err(ProgramError::InvalidAccountData),
        };

        Ok(Self {
            mint,
            owner,
            amount,
            delegate: COption::None,
            state,
            is_native: COption::None,
            delegated_amount: 0,
            close_authority: COption::None,
        })
    }

    fn unpack_unchecked(data: &[u8]) -> Result<Self, ProgramError> {
        Self::unpack_from_slice(data)
    }
}

#[inline(never)]
fn get_account(acc: &AccountInfo<'_>) -> Result<Account, ProgramError> {
    Account::unpack_unchecked(&acc.data.borrow())
}
