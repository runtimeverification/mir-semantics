use std::cell::RefCell;
use std::convert::TryInto;
use std::rc::Rc;

const TOKEN_PROGRAM_ID: Pubkey = Pubkey::from_array([
    6, 221, 246, 225, 215, 101, 161, 147, 217, 203, 225, 70, 206, 235, 121, 172, 28, 180, 133, 237, 95, 91, 55, 145, 58, 140, 245, 133, 126, 255, 0, 169,
]);
const SYSVAR_RENT_ID: Pubkey = Pubkey::from_array([
    6, 167, 213, 23, 25, 44, 92, 81, 33, 140, 201, 76, 61, 74, 241, 127, 88, 218, 238, 8, 155, 161, 253, 68, 227, 219, 217, 138, 0, 0, 0, 0,
]);
const SYSVAR_OWNER_ID: Pubkey = Pubkey::from_array([
    0, 0, 2, 60, 76, 124, 176, 94, 224, 136, 161, 229, 55, 148, 115, 140, 52, 37, 150, 11, 228, 174, 241, 188, 101, 179, 155, 28, 0, 0, 0, 0,
]);
const ACCOUNT_KEY: Pubkey = Pubkey::from_array([9; 32]);
const ACCOUNT_OWNER: Pubkey = Pubkey::from_array([8; 32]);
const ACCOUNT_DELEGATE: Pubkey = Pubkey::from_array([12; 32]);
const ACCOUNT_CLOSE_AUTHORITY: Pubkey = Pubkey::from_array([13; 32]);
const MINT_KEY: Pubkey = Pubkey::from_array([10; 32]);
const MINT_AUTHORITY: Pubkey = Pubkey::from_array([14; 32]);
const FREEZE_AUTHORITY: Pubkey = Pubkey::from_array([15; 32]);
const MULTISIG_KEY: Pubkey = Pubkey::from_array([11; 32]);
const MULTISIG_SIGNER_A: Pubkey = Pubkey::from_array([16; 32]);
const MULTISIG_SIGNER_B: Pubkey = Pubkey::from_array([17; 32]);
const MULTISIG_SIGNER_C: Pubkey = Pubkey::from_array([18; 32]);
const ACCOUNT_LAMPORTS: u64 = 1_000_000;
const RENT_LAMPORTS: u64 = 1;

fn main() {
    let base_account = Account::default();
    let mut acc_data = [0u8; Account::LEN];
    let mut account_lamports = ACCOUNT_LAMPORTS;
    let acc = AccountInfo::from_account(
        base_account.clone(),
        &mut acc_data[..],
        &ACCOUNT_KEY,
        &TOKEN_PROGRAM_ID,
        &mut account_lamports,
    );

    let mut mint_data = [0u8; Mint::LEN];
    Mint::pack(&Mint::default(), &mut mint_data).unwrap();
    let mut mint_lamports = 0;
    let mint = AccountInfo::from_data(&mut mint_data[..], &MINT_KEY, &TOKEN_PROGRAM_ID, &mut mint_lamports);

    let mut multisig_data = [0u8; Multisig::LEN];
    Multisig::pack(&Multisig::default(), &mut multisig_data).unwrap();
    let mut multisig_lamports = 0;
    let multisig =
        AccountInfo::from_data(&mut multisig_data[..], &MULTISIG_KEY, &TOKEN_PROGRAM_ID, &mut multisig_lamports);

    let mut rent_data = [0u8; Rent::LEN];
    Rent::pack(&Rent::default(), &mut rent_data).unwrap();
    let mut rent_lamports = RENT_LAMPORTS;
    let rent = AccountInfo::new(
        &SYSVAR_RENT_ID,
        &mut rent_lamports,
        &mut rent_data[..],
        &SYSVAR_OWNER_ID,
        0,
        false,
        false,
        false,
    );

    test_spltoken_domain_data(&acc, &mint, &multisig, &rent);
    // Keep lamports read/write harness reachable so stable-mir emits it.
    test_spl_account_lamports_read_then_write(&[acc.clone()]);
}

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

impl<'a> AccountInfo<'a> {
    fn from_account(
        account: Account,
        data: &'a mut [u8],
        key: &'a Pubkey,
        owner: &'a Pubkey,
        lamports: &'a mut u64,
    ) -> Self {
        Account::pack(&account, data).unwrap();
        Self::from_data(data, key, owner, lamports)
    }

    fn from_data(
        data: &'a mut [u8],
        key: &'a Pubkey,
        owner: &'a Pubkey,
        lamports: &'a mut u64,
    ) -> Self {
        Self::new(key, lamports, data, owner, 0, false, true, false)
    }

    fn new(
        key: &'a Pubkey,
        lamports: &'a mut u64,
        data: &'a mut [u8],
        owner: &'a Pubkey,
        rent_epoch: u64,
        is_signer: bool,
        is_writable: bool,
        executable: bool,
    ) -> Self {
        Self {
            key,
            lamports: Rc::new(RefCell::new(lamports)),
            data: Rc::new(RefCell::new(data)),
            owner,
            rent_epoch,
            is_signer,
            is_writable,
            executable,
        }
    }

    fn data_len(&self) -> usize {
        self.data.borrow().len()
    }
}

fn test_spltoken_domain_data(
    acc: &AccountInfo<'_>,
    mint: &AccountInfo<'_>,
    multisig: &AccountInfo<'_>,
    rent: &AccountInfo<'_>,
) {
    test_spl_account_domain_data(acc);
    test_spl_mint_domain_data(mint);
    test_spl_multisig_domain_data(multisig);
    test_spl_rent_domain_data(rent);
}

fn test_spl_account_domain_data(acc: &AccountInfo<'_>) {
    cheatcode_is_spl_account(acc);

    let owner = acc.owner;
    assert_eq!(acc.owner, owner);

    let mut account = get_account(acc);
    account.is_native = COption::Some(0);
    account.mint = MINT_KEY;
    account.owner = ACCOUNT_OWNER;
    account.amount = 123_456;
    account.delegate = COption::Some(ACCOUNT_DELEGATE);
    account.state = AccountState::Initialized;
    account.delegated_amount = 789;
    account.close_authority = COption::Some(ACCOUNT_CLOSE_AUTHORITY);
    Account::pack(&account, &mut acc.data.borrow_mut()).unwrap();
    let unpacked_account = get_account(acc);
    assert!(unpacked_account.is_native());
    assert_eq!(unpacked_account.mint, MINT_KEY);
    assert_eq!(unpacked_account.owner, ACCOUNT_OWNER);
    assert_eq!(unpacked_account.amount, 123_456);
    assert_eq!(unpacked_account.delegate, COption::Some(ACCOUNT_DELEGATE));
    assert_eq!(unpacked_account.close_authority, COption::Some(ACCOUNT_CLOSE_AUTHORITY));
    assert_eq!(unpacked_account.state, AccountState::Initialized);
}

fn test_spl_mint_domain_data(mint: &AccountInfo<'_>) {
    cheatcode_is_spl_mint(mint);

    assert_eq!(mint.data_len(), Mint::LEN);

    let mut mint_state = get_mint(mint);
    mint_state.is_initialized = true;
    mint_state.supply = 42;
    mint_state.decimals = 9;
    mint_state.mint_authority = COption::Some(MINT_AUTHORITY);
    mint_state.freeze_authority = COption::Some(FREEZE_AUTHORITY);
    Mint::pack(&mint_state, &mut mint.data.borrow_mut()).unwrap();
    let unpacked_mint = get_mint(mint);
    assert!(unpacked_mint.is_initialized);
    assert_eq!(unpacked_mint.supply, 42);
    assert_eq!(unpacked_mint.decimals, 9);
    assert_eq!(unpacked_mint.mint_authority, COption::Some(MINT_AUTHORITY));
    assert_eq!(unpacked_mint.freeze_authority, COption::Some(FREEZE_AUTHORITY));
}

fn test_spl_multisig_domain_data(multisig: &AccountInfo<'_>) {
    cheatcode_is_spl_multisig(multisig);

    let mut multisig_state = get_multisig(multisig);
    assert!(!multisig_state.is_initialized);
    multisig_state.is_initialized = true;
    multisig_state.m = 2;
    multisig_state.n = 3;
    multisig_state.signers[0] = MULTISIG_SIGNER_A;
    multisig_state.signers[1] = MULTISIG_SIGNER_B;
    multisig_state.signers[2] = MULTISIG_SIGNER_C;
    Multisig::pack(&multisig_state, &mut multisig.data.borrow_mut()).unwrap();
    let unpacked_multisig = get_multisig(multisig);
    assert!(unpacked_multisig.is_initialized);
    assert_eq!(unpacked_multisig.m, 2);
    assert_eq!(unpacked_multisig.n, 3);
    assert_eq!(unpacked_multisig.signers[0], MULTISIG_SIGNER_A);
    assert_eq!(unpacked_multisig.signers[1], MULTISIG_SIGNER_B);
    assert_eq!(unpacked_multisig.signers[2], MULTISIG_SIGNER_C);
}

/// Read symbolic lamports, write a concrete value, then read again to mirror the close_account stuck case and ensure writes propagate.
#[inline(never)]
fn test_spl_account_lamports_read_then_write(accounts: &[AccountInfo; 1]) -> (u64, u64) {
    cheatcode_is_spl_account(&accounts[0]);
    let before = **accounts[0].lamports.borrow();
    **accounts[0].lamports.borrow_mut() = 42;
    let after = **accounts[0].lamports.borrow();
    (before, after)
}

fn test_spl_rent_domain_data(rent: &AccountInfo<'_>) {
    // Compare rent burn semantics with the canonical sysvar value
    let sysrent = Rent::get().unwrap();
    let rent_collected = 10;
    let (sys_burnt, sys_distributed) = sysrent.calculate_burn(rent_collected);
    assert!(sysrent.burn_percent > 100 || (sys_burnt <= rent_collected && sys_distributed <= rent_collected));

    cheatcode_is_spl_rent(rent);
    assert_eq!(rent.data_len(), Rent::LEN);
    let prent = Rent::from_account_info(rent).unwrap_or(sysrent);
    let (acct_burnt, acct_distributed) = prent.calculate_burn(rent_collected);
    assert!(prent.burn_percent > 100 || (acct_burnt <= rent_collected && acct_distributed <= rent_collected));
}

fn get_account(acc: &AccountInfo<'_>) -> Account {
    Account::unpack_unchecked(&acc.data.borrow()).unwrap()
}

fn get_mint(acc: &AccountInfo<'_>) -> Mint {
    Mint::unpack_unchecked(&acc.data.borrow()).unwrap()
}

fn get_multisig(acc: &AccountInfo<'_>) -> Multisig {
    Multisig::unpack_unchecked(&acc.data.borrow()).unwrap()
}

#[inline(never)]
fn cheatcode_is_spl_account(_: &AccountInfo<'_>) {}

#[inline(never)]
fn cheatcode_is_spl_mint(_: &AccountInfo<'_>) {}

#[inline(never)]
fn cheatcode_is_spl_multisig(_: &AccountInfo<'_>) {}

#[inline(never)]
fn cheatcode_is_spl_rent(_: &AccountInfo<'_>) {}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Pubkey([u8; 32]);

impl Pubkey {
    const fn from_array(bytes: [u8; 32]) -> Self {
        Self(bytes)
    }

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

    fn unpack_from_slice(data: &[u8]) -> Result<Self, ProgramError> {
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

    fn unpack_unchecked(data: &[u8]) -> Result<Self, ProgramError> {
        Self::unpack_from_slice(data)
    }

    fn pack_into_slice(&self, dst: &mut [u8]) {
        dst[0..32].copy_from_slice(self.mint.as_ref());
        dst[32..64].copy_from_slice(self.owner.as_ref());
        dst[64..72].copy_from_slice(&self.amount.to_le_bytes());
        encode_coption_key(&self.delegate, &mut dst[72..108]);
        dst[108] = self.state as u8;
        encode_coption_u64(&self.is_native, &mut dst[109..121]);
        dst[121..129].copy_from_slice(&self.delegated_amount.to_le_bytes());
        encode_coption_key(&self.close_authority, &mut dst[129..165]);
    }

    fn pack(account: &Account, dst: &mut [u8]) -> Result<(), ProgramError> {
        if dst.len() < Self::LEN {
            return Err(ProgramError::InvalidAccountData);
        }
        account.pack_into_slice(dst);
        Ok(())
    }
}

#[derive(Clone, Debug)]
struct Mint {
    mint_authority: COption<Pubkey>,
    supply: u64,
    decimals: u8,
    is_initialized: bool,
    freeze_authority: COption<Pubkey>,
}

impl Default for Mint {
    fn default() -> Self {
        Self {
            mint_authority: COption::None,
            supply: 0,
            decimals: 0,
            is_initialized: false,
            freeze_authority: COption::None,
        }
    }
}

impl Mint {
    const LEN: usize = 82;

    fn unpack_from_slice(data: &[u8]) -> Result<Self, ProgramError> {
        if data.len() < Self::LEN {
            return Err(ProgramError::InvalidAccountData);
        }
        let mint_authority = decode_coption_key(&data[0..36])?;
        let supply = u64::from_le_bytes(data[36..44].try_into().unwrap());
        let decimals = data[44];
        let is_initialized = match data[45] {
            0 => false,
            1 => true,
            _ => return Err(ProgramError::InvalidAccountData),
        };
        let freeze_authority = decode_coption_key(&data[46..82])?;
        Ok(Self {
            mint_authority,
            supply,
            decimals,
            is_initialized,
            freeze_authority,
        })
    }

    fn unpack_unchecked(data: &[u8]) -> Result<Self, ProgramError> {
        Self::unpack_from_slice(data)
    }

    fn pack_into_slice(&self, dst: &mut [u8]) {
        encode_coption_key(&self.mint_authority, &mut dst[0..36]);
        dst[36..44].copy_from_slice(&self.supply.to_le_bytes());
        dst[44] = self.decimals;
        dst[45] = self.is_initialized as u8;
        encode_coption_key(&self.freeze_authority, &mut dst[46..82]);
    }

    fn pack(mint: &Mint, dst: &mut [u8]) -> Result<(), ProgramError> {
        if dst.len() < Self::LEN {
            return Err(ProgramError::InvalidAccountData);
        }
        mint.pack_into_slice(dst);
        Ok(())
    }
}

const MAX_SIGNERS: usize = 11;

#[derive(Clone, Debug)]
struct Multisig {
    m: u8,
    n: u8,
    is_initialized: bool,
    signers: [Pubkey; MAX_SIGNERS],
}

impl Default for Multisig {
    fn default() -> Self {
        Self {
            m: 0,
            n: 0,
            is_initialized: false,
            signers: [Pubkey::new([0; 32]); MAX_SIGNERS],
        }
    }
}

impl Multisig {
    const LEN: usize = 355;

    fn unpack_from_slice(data: &[u8]) -> Result<Self, ProgramError> {
        if data.len() < Self::LEN {
            return Err(ProgramError::InvalidAccountData);
        }
        let m = data[0];
        let n = data[1];
        let is_initialized = match data[2] {
            0 => false,
            1 => true,
            _ => return Err(ProgramError::InvalidAccountData),
        };
        let mut signers = [Pubkey::new([0; 32]); MAX_SIGNERS];
        for (i, slot) in signers.iter_mut().enumerate() {
            let start = 3 + i * 32;
            let end = start + 32;
            *slot = Pubkey::new(data[start..end].try_into().unwrap());
        }
        Ok(Self {
            m,
            n,
            is_initialized,
            signers,
        })
    }

    fn unpack_unchecked(data: &[u8]) -> Result<Self, ProgramError> {
        Self::unpack_from_slice(data)
    }

    fn pack_into_slice(&self, dst: &mut [u8]) {
        dst[0] = self.m;
        dst[1] = self.n;
        dst[2] = self.is_initialized as u8;
        for (i, signer) in self.signers.iter().enumerate() {
            let start = 3 + i * 32;
            dst[start..start + 32].copy_from_slice(signer.as_ref());
        }
    }

    fn pack(multisig: &Multisig, dst: &mut [u8]) -> Result<(), ProgramError> {
        if dst.len() < Self::LEN {
            return Err(ProgramError::InvalidAccountData);
        }
        multisig.pack_into_slice(dst);
        Ok(())
    }
}

#[derive(Clone, Copy, Debug)]
struct Rent {
    lamports_per_byte_year: u64,
    exemption_threshold: f64,
    burn_percent: u8,
}

impl Default for Rent {
    fn default() -> Self {
        Self {
            lamports_per_byte_year: Rent::DEFAULT_LAMPORTS_PER_BYTE_YEAR,
            exemption_threshold: Rent::DEFAULT_EXEMPTION_THRESHOLD,
            burn_percent: Rent::DEFAULT_BURN_PERCENT,
        }
    }
}

impl Rent {
    const LEN: usize = 17;
    const ACCOUNT_STORAGE_OVERHEAD: u64 = 128;
    const DEFAULT_LAMPORTS_PER_BYTE_YEAR: u64 = 1_000_000_000 / 100 * 365 / (1024 * 1024);
    const DEFAULT_EXEMPTION_THRESHOLD: f64 = 2.0;
    const DEFAULT_EXEMPTION_THRESHOLD_AS_U64: u64 = 2;
    const DEFAULT_BURN_PERCENT: u8 = 50;

    fn minimum_balance(&self, data_len: usize) -> u64 {
        let bytes = data_len as u64;
        let base = (Self::ACCOUNT_STORAGE_OVERHEAD + bytes) * self.lamports_per_byte_year;
        if self.exemption_threshold == Self::DEFAULT_EXEMPTION_THRESHOLD {
            base * Self::DEFAULT_EXEMPTION_THRESHOLD_AS_U64
        } else {
            (base as f64 * self.exemption_threshold) as u64
        }
    }

    fn calculate_burn(&self, rent_collected: u64) -> (u64, u64) {
        let burned = (rent_collected * u64::from(self.burn_percent)) / 100;
        (burned, rent_collected - burned)
    }

    fn unpack(data: &[u8]) -> Result<Self, ProgramError> {
        if data.len() < Self::LEN {
            return Err(ProgramError::InvalidAccountData);
        }
        let lamports_per_byte_year = u64::from_le_bytes(data[0..8].try_into().unwrap());
        let exemption_threshold = f64::from_le_bytes(data[8..16].try_into().unwrap());
        let burn_percent = data[16];
        Ok(Self {
            lamports_per_byte_year,
            exemption_threshold,
            burn_percent,
        })
    }

    fn pack(rent: &Rent, dst: &mut [u8]) -> Result<(), ProgramError> {
        if dst.len() < Self::LEN {
            return Err(ProgramError::InvalidAccountData);
        }
        dst[0..8].copy_from_slice(&rent.lamports_per_byte_year.to_le_bytes());
        dst[8..16].copy_from_slice(&rent.exemption_threshold.to_le_bytes());
        dst[16] = rent.burn_percent;
        Ok(())
    }

    fn from_account_info(account_info: &AccountInfo<'_>) -> Result<Self, ProgramError> {
        if account_info.key != &SYSVAR_RENT_ID {
            return Err(ProgramError::InvalidAccountData);
        }
        Self::unpack(&account_info.data.borrow())
    }

    fn get() -> Result<Self, ProgramError> {
        // In production this pulls from the rent sysvar; for the harness we use the default
        Ok(Self::default())
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
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
