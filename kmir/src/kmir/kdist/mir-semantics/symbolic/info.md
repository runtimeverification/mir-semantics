**AccountInfo**
- P-Token: `pinocchio::account_info::AccountInfo` stores its data in two layers:
  - `Account` (raw bytes, borrow state, Pubkey, etc.)
  - `AccountInfo`, which merely keeps a raw pointer to it
  - See `pinocchio-0.9.0/src/account_info.rs:18-120`.  
```rust
#[repr(C)]
pub(crate) struct Account {
    pub(crate) borrow_state: u8,
    is_signer: u8,
    is_writable: u8,
    executable: u8,
    resize_delta: i32,
    key: Pubkey,
    owner: Pubkey,
    lamports: u64,
    pub(crate) data_len: u64,
}

#[repr(C)]
#[derive(Clone, PartialEq, Eq)]
pub struct AccountInfo {
    pub(crate) raw: *mut Account,
}
```
Every `AccountInfo` method (`key()`, `owner()`, `lamports()`, etc.) directly dereferences with `unsafe { (*self.raw).... }`, so the Pinocchio pipeline’s `load::<T>` can reinterpret `AccountInfo.data` as a `#[repr(C)]` struct while remaining consistent with the borrow flags.
- SPL Token: `solana_account_info::AccountInfo<'a>` exposes every field and wraps lamports/data inside `Rc<RefCell<...>>`, integrating with the runtime `next_account_info`/`Pack` borrow checks (see `solana-account-info-2.3.0/src/lib.rs:15-56`).  
```rust
#[derive(Clone)]
#[repr(C)]
pub struct AccountInfo<'a> {
    pub key: &'a Pubkey,
    pub lamports: Rc<RefCell<&'a mut u64>>,
    pub data: Rc<RefCell<&'a mut [u8]>>,
    pub owner: &'a Pubkey,
    pub rent_epoch: u64,
    pub is_signer: bool,
    pub is_writable: bool,
    pub executable: bool,
}
```
The Solana implementation relies on `RefCell::try_borrow(_mut)` to return `Ref`/`RefMut`, so processors receive runtime borrow errors whenever they call `AccountInfo.data.borrow_mut()` after `next_account_info`.

**Data parsing utilities (COption / Transmutable / Pack)**
- P-Token: `p-interface/src/state/mod.rs:8-97` defines `COption<T> = ([u8; 4], T)`, `Transmutable`, `load/load_mut`, and `Initializable`. Length constants and byte-copy checks ensure that `AccountInfo` data matches the structure layout exactly, which removes the need for `Pack`.  
```rust
// p-interface/src/state/mod.rs:8-97
pub type COption<T> = ([u8; 4], T);
pub unsafe trait Transmutable { const LEN: usize; }
pub trait Initializable { fn is_initialized(&self) -> Result<bool, ProgramError>; }
pub unsafe fn load<T: Initializable + Transmutable>(bytes: &[u8]) -> Result<&T, ProgramError> { … }
pub unsafe fn load_mut<T: Initializable + Transmutable>(bytes: &mut [u8]) -> Result<&mut T, ProgramError> { … }
```
- SPL Token: `interface/src/state.rs:13-107` uses `solana_program_option::COption` together with the `Pack`/`IsInitialized` traits. `Pack::LEN`, `pack_into_slice`, and `unpack_from_slice` perform safe serialization on the `RefCell<[u8]>` inside `AccountInfo`.  
```rust
// interface/src/state.rs:13-107
use {
    arrayref::{array_mut_ref, array_ref, array_refs, mut_array_refs},
    solana_program_pack::{IsInitialized, Pack, Sealed},
};
```

**Account structure**
- P-Token: `p-interface/src/state/account.rs:13-152` stores every numeric value inside `[u8; N]` fields, exposes getters/setters to interpret the slices as `u64` or `COption`, and implements `Transmutable + Initializable` so it can be passed to `load`.  
```rust
// p-interface/src/state/account.rs:13-152
#[repr(C)]
pub struct Account {
    pub mint: Pubkey,
    pub owner: Pubkey,
    amount: [u8; 8],
    delegate: COption<Pubkey>,
    state: u8,
    is_native: [u8; 4],
    native_amount: [u8; 8],
    delegated_amount: [u8; 8],
    close_authority: COption<Pubkey>,
}
impl Account {
    pub fn amount(&self) -> u64 { … }
    pub fn delegate(&self) -> Option<&Pubkey> { … }
    pub fn native_amount(&self) -> Option<u64> { … }
}
```
- SPL Token: `interface/src/state.rs:109-190` exposes `pub` fields and implements `Pack`. It uses the `arrayref` macros to read/write `u64` and `COption` at fixed offsets and also provides a default implementation of `GenericTokenAccount`.  
```rust
// interface/src/state.rs:109-190
#[repr(C)]
pub struct Account {
    pub mint: Pubkey,
    pub owner: Pubkey,
    pub amount: u64,
    pub delegate: COption<Pubkey>,
    pub state: AccountState,
    pub is_native: COption<u64>,
    pub delegated_amount: u64,
    pub close_authority: COption<Pubkey>,
}
impl Pack for Account {
    const LEN: usize = 165;
    fn unpack_from_slice(src: &[u8]) -> Result<Self, ProgramError> { … }
    fn pack_into_slice(&self, dst: &mut [u8]) { … }
}
```

**AccountState enum**
- P-Token: `p-interface/src/state/account_state.rs:3-29` uses `#[repr(u8)]` and `TryFrom<u8>` to convert between raw bytes and semantic variants, and implements `Initializable` detection.  
```rust
// p-interface/src/state/account_state.rs:3-29
#[repr(u8)]
pub enum AccountState { Uninitialized, Initialized, Frozen }
impl TryFrom<u8> for AccountState { type Error = ProgramError; fn try_from(value: u8) -> Result<Self, ProgramError> { … } }
```
- SPL Token: `interface/src/state.rs:83-107` also declares `AccountState` as `#[repr(u8)]`, but implements `Pack`/`Sealed`’s `IsInitialized`, which `Account` relies on for serialization.  
```rust
// interface/src/state.rs:83-107
#[repr(u8)]
pub enum AccountState { Uninitialized, Initialized, Frozen }
impl IsInitialized for AccountState { fn is_initialized(&self) -> bool { matches!(self, Self::Initialized | Self::Frozen) } }
```

**Mint structure**
- P-Token: `p-interface/src/state/mint.rs:6-84` stores `supply`, `native_amount`, and similar fields as `[u8; 8]`, exposes methods that convert them to `u64`, and keeps `freeze_authority`/`mint_authority` as `COption<Pubkey>` to keep `Transmutable`’s length fixed.  
```rust
// p-interface/src/state/mint.rs:6-84
#[repr(C)]
pub struct Mint {
    mint_authority: COption<Pubkey>,
    supply: [u8; 8],
    pub decimals: u8,
    is_initialized: u8,
    freeze_authority: COption<Pubkey>,
}
impl Mint { pub fn supply(&self) -> u64 { … } pub fn mint_authority(&self) -> Option<&Pubkey> { … } }
```
- SPL Token: `interface/src/state.rs:13-82` keeps fields such as `supply: u64` and `is_initialized: bool` as semantic types and writes them into a fixed-size array via `Pack`.  
```rust
// interface/src/state.rs:13-82
#[repr(C)]
pub struct Mint {
    pub mint_authority: COption<Pubkey>,
    pub supply: u64,
    pub decimals: u8,
    pub is_initialized: bool,
    pub freeze_authority: COption<Pubkey>,
}
impl Pack for Mint { const LEN: usize = 82; fn pack_into_slice(&self, dst: &mut [u8]) { … } }
```

**Multisig structure**
- P-Token: `p-interface/src/state/multisig.rs:6-55` fixes `MAX_SIGNERS: u8 = 11`, stores `m/n` and `[Pubkey; MAX_SIGNERS as usize]` in a `#[repr(C)]` struct, and exposes helpers for validating signer indices.  
```rust
// p-interface/src/state/multisig.rs:6-55
pub const MAX_SIGNERS: u8 = 11;
#[repr(C)]
pub struct Multisig {
    pub m: u8,
    pub n: u8,
    is_initialized: u8,
    pub signers: [Pubkey; MAX_SIGNERS as usize],
}
impl Multisig { pub fn is_valid_signer_index(index: u8) -> bool { … } }
```
- SPL Token: `interface/src/state.rs:199-249` uses the same fields but relies on `Pack`, explicitly sets `LEN = 355`, and calls the `array_refs!` macro inside `pack/unpack` to slice the account data.  
```rust
// interface/src/state.rs:199-249
#[repr(C)]
pub struct Multisig {
    pub m: u8,
    pub n: u8,
    pub is_initialized: bool,
    pub signers: [Pubkey; MAX_SIGNERS],
}
impl Pack for Multisig {
    const LEN: usize = 355;
    fn unpack_from_slice(src: &[u8]) -> Result<Self, ProgramError> { … }
    fn pack_into_slice(&self, dst: &mut [u8]) { … }
}
```

**Helper readers / validators**
- P-Token: `p-token/src/processor/mod.rs:89-138` defines `check_account_owner` and `validate_owner` that operate directly on `AccountInfo` buffers using pointer/slice arithmetic, reusing `load::<Multisig>` and related helpers to validate multisig signers.  
```rust
// p-token/src/processor/mod.rs:89-138
#[inline(always)]
fn check_account_owner(account_info: &AccountInfo) -> ProgramResult { … }
#[inline(always)]
unsafe fn validate_owner(
    expected_owner: &Pubkey,
    owner_account_info: &AccountInfo,
    signers: &[AccountInfo],
) -> ProgramResult { … }
```
- SPL Token: `interface/src/state.rs:252-357` supplies helpers such as `pack_coption_*`, `GenericTokenAccount`, and `ACCOUNT_INITIALIZED_INDEX`, so callers can validate `owner/mint` or initialization status via offsets without fully unpacking the account.  
```rust
// interface/src/state.rs:294-357
pub trait GenericTokenAccount {
    fn valid_account_data(account_data: &[u8]) -> bool;
    fn unpack_account_owner_unchecked(account_data: &[u8]) -> &Pubkey { … }
    fn unpack_account_mint_unchecked(account_data: &[u8]) -> &Pubkey { … }
}
pub const ACCOUNT_INITIALIZED_INDEX: usize = 108;
pub fn is_initialized_account(account_data: &[u8]) -> bool { … }
```

**Key differences**
- `AccountInfo` usage: P-Token relies entirely on Pinocchio’s raw-pointer-based `AccountInfo`, while SPL uses the Solana SDK with `RefCell`, sysvars, and `Pack`.
- Serialization strategy: P-Token enforces a one-to-one layout between structs and account bytes via `Transmutable`, whereas SPL declares size/offsets through `Pack`, allowing the `RefCell` buffer to copy data.
- Optional fields: P-Token implements its own `[u8; 4]`-tagged `COption`, while SPL reuses `solana_program_option::COption` plus the `Pack` helpers.
- Field visibility: P-Token prevents direct mutation of internal `[u8; N]` slices, whereas SPL makes the main fields `pub` and leans on the `Pack` implementation for consistency.
- Metadata extraction: SPL adds helpers such as `GenericTokenAccount` and `ACCOUNT_INITIALIZED_INDEX` for CPI/clients to read owner/mint quickly, while P-Token depends on `load`-based reinterprets and custom validators.
