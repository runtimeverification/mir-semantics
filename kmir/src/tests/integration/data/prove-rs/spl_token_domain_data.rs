use std::cell::RefCell;
use std::convert::TryInto;
use std::rc::Rc;

fn main() {
    let base_account = Account::default();
    let mut data = [0u8; Account::LEN];
    let acc = AccountInfo::from_account(base_account.clone(), &mut data[..]);
    // Mirror the SPL runtime harness: same account for all three params.
    test_spltoken_domain_data(&acc, &acc, &acc);
}

#[derive(Clone)]
struct AccountInfo<'a> {
    key: Pubkey,
    lamports: Rc<RefCell<u64>>,
    data: Rc<RefCell<&'a mut [u8]>>,
    owner: Pubkey,
    rent_epoch: u64,
    is_signer: bool,
    is_writable: bool,
    executable: bool,
}

impl<'a> AccountInfo<'a> {
    fn from_account(account: Account, data: &'a mut [u8]) -> Self {
        Account::pack(account, data).unwrap();
        Self {
            key: Pubkey::new([0; 32]),
            lamports: Rc::new(RefCell::new(0)),
            data: Rc::new(RefCell::new(data)),
            owner: Pubkey::new([1; 32]),
            rent_epoch: 0,
            is_signer: false,
            is_writable: true,
            executable: false,
        }
    }
}

fn test_spltoken_domain_data(acc: &AccountInfo<'_>, _mint: &AccountInfo<'_>, _rent: &AccountInfo<'_>) {
    cheatcode_is_spl_account(acc);

    let mut account = get_account(acc);
    
    account.is_native = COption::Some(0);
    assert!(account.is_native());
    
    Account::pack(account, &mut acc.data.borrow_mut()).unwrap();

    let unpacked = get_account(acc);
    assert!(unpacked.is_native());
}

fn get_account(acc: &AccountInfo<'_>) -> Account {
    Account::unpack_unchecked(&acc.data.borrow()).unwrap()
}

#[inline(never)]
fn cheatcode_is_spl_account(_: &AccountInfo<'_>) {}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Pubkey([u8; 32]);

impl Pubkey {
    fn new(bytes: [u8; 32]) -> Self {
        Self(bytes)
    }

    fn as_ref(&self) -> &[u8; 32] {
        &self.0
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum ProgramError {
    InvalidAccountData,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum AccountState {
    Uninitialized = 0,
    Initialized = 1,
    Frozen = 2,
}

#[derive(Clone, Debug)]
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

impl Default for Account {
    fn default() -> Self {
        Self {
            mint: Pubkey::new([2; 32]),
            owner: Pubkey::new([3; 32]),
            amount: 0,
            delegate: COption::None,
            state: AccountState::Uninitialized,
            is_native: COption::None,
            delegated_amount: 0,
            close_authority: COption::None,
        }
    }
}

impl Account {
    const LEN: usize = 165;

    fn is_native(&self) -> bool {
        matches!(self.is_native, COption::Some(_))
    }

    fn unpack_unchecked(data: &[u8]) -> Result<Self, ProgramError> {
        if data.len() < Self::LEN {
            return Err(ProgramError::InvalidAccountData);
        }
        let mint = Pubkey::new(data[0..32].try_into().unwrap());
        let owner = Pubkey::new(data[32..64].try_into().unwrap());
        let amount = u64::from_le_bytes(data[64..72].try_into().unwrap());
        let delegate = decode_coption_key(&data[72..108])?;
        let state = match data[108] {
            0 => AccountState::Uninitialized,
            1 => AccountState::Initialized,
            2 => AccountState::Frozen,
            _ => return Err(ProgramError::InvalidAccountData),
        };
        let is_native = decode_coption_u64(&data[109..121])?;
        let delegated_amount = u64::from_le_bytes(data[121..129].try_into().unwrap());
        let close_authority = decode_coption_key(&data[129..165])?;

        Ok(Self {
            mint,
            owner,
            amount,
            delegate,
            state,
            is_native,
            delegated_amount,
            close_authority,
        })
    }

    fn pack(account: Account, dst: &mut [u8]) -> Result<(), ProgramError> {
        if dst.len() < Self::LEN {
            return Err(ProgramError::InvalidAccountData);
        }
        dst[0..32].copy_from_slice(account.mint.as_ref());
        dst[32..64].copy_from_slice(account.owner.as_ref());
        dst[64..72].copy_from_slice(&account.amount.to_le_bytes());
        encode_coption_key(&account.delegate, &mut dst[72..108]);
        dst[108] = account.state as u8;
        encode_coption_u64(&account.is_native, &mut dst[109..121]);
        dst[121..129].copy_from_slice(&account.delegated_amount.to_le_bytes());
        encode_coption_key(&account.close_authority, &mut dst[129..165]);
        Ok(())
    }
}

#[derive(Clone, Debug)]
enum COption<T> {
    None,
    Some(T),
}

fn decode_coption_key(bytes: &[u8]) -> Result<COption<Pubkey>, ProgramError> {
    let tag = &bytes[0..4];
    match tag {
        [0, 0, 0, 0] => Ok(COption::None),
        [1, 0, 0, 0] => Ok(COption::Some(Pubkey::new(bytes[4..36].try_into().unwrap()))),
        _ => Err(ProgramError::InvalidAccountData),
    }
}

fn decode_coption_u64(bytes: &[u8]) -> Result<COption<u64>, ProgramError> {
    let tag = &bytes[0..4];
    match tag {
        [0, 0, 0, 0] => Ok(COption::None),
        [1, 0, 0, 0] => Ok(COption::Some(u64::from_le_bytes(bytes[4..12].try_into().unwrap()))),
        _ => Err(ProgramError::InvalidAccountData),
    }
}

fn encode_coption_key(src: &COption<Pubkey>, dst: &mut [u8]) {
    match src {
        COption::None => {
            dst[0..4].copy_from_slice(&[0; 4]);
            dst[4..36].fill(0);
        }
        COption::Some(key) => {
            dst[0..4].copy_from_slice(&[1, 0, 0, 0]);
            dst[4..36].copy_from_slice(key.as_ref());
        }
    }
}

fn encode_coption_u64(src: &COption<u64>, dst: &mut [u8]) {
    match src {
        COption::None => {
            dst[0..4].copy_from_slice(&[0; 4]);
            dst[4..12].fill(0);
        }
        COption::Some(amount) => {
            dst[0..4].copy_from_slice(&[1, 0, 0, 0]);
            dst[4..12].copy_from_slice(&amount.to_le_bytes());
        }
    }
}
