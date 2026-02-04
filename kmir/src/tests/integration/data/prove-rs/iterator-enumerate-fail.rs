pub const PUBKEY_BYTES: usize = 32;

pub type Pubkey = [u8; PUBKEY_BYTES];

#[repr(C)]
#[derive(Clone, Copy, Default)]
pub(crate) struct Account {
    key: Pubkey,
}

#[repr(C)]
#[derive(Clone, PartialEq, Eq)]
pub struct AccountInfo {
    pub(crate) raw: *mut Account,
}

impl AccountInfo {
    #[inline(always)]
    pub fn key(&self) -> &Pubkey {
        unsafe { &(*self.raw).key }
    }
}

pub const MAX_SIGNERS: u8 = 2;

#[repr(C)]
pub struct Multisig {
    pub signers: [Pubkey; MAX_SIGNERS as usize],
}

fn main() {
    let mut acc1 = Account { key: [1; 32] };
    let mut acc2 = Account { key: [2; 32] };

    let info1 = AccountInfo { raw: &mut acc1 as *mut Account };
    let info2 = AccountInfo { raw: &mut acc2 as *mut Account };

    let accounts = [info1, info2];

    process(&accounts);
}

fn process(accounts: &[AccountInfo]) {
    assert_eq!(*accounts[0].key(), [1_u8; 32]);
    assert_eq!(*accounts[1].key(), [2_u8; 32]);

    let multisig = &mut Multisig { signers: [ [0; 32]; 2] };
              // Two zero initialised Pubkeys ^^^^^^^^^^^

    for (i, signer_info) in accounts.iter().enumerate() {
        multisig.signers[i] = *signer_info.key();
    }
}
