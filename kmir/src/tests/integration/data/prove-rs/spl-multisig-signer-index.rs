use std::cell::RefCell;
use std::convert::TryInto;
use std::rc::Rc;

fn main() {
    let _keep: fn(&AccountInfo<'_>, Pubkey) = repro;
}

#[inline(never)]
#[no_mangle]
pub fn repro(multisig_acc: &AccountInfo<'_>, replacement: Pubkey) {
    cheatcode_is_spl_multisig(multisig_acc);
    let mut multisig_state = Multisig::unpack_unchecked(&multisig_acc.data.borrow()).unwrap();
    let signer_idx = 0usize;
    multisig_state.signers[signer_idx] = replacement;
    assert_eq!(multisig_state.signers[signer_idx], replacement);
}

#[inline(never)]
fn cheatcode_is_spl_multisig(_: &AccountInfo<'_>) {}

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
}

const MAX_SIGNERS: usize = 3;

#[derive(Clone, Debug)]
struct Multisig {
    m: u8,
    n: u8,
    is_initialized: bool,
    signers: [Pubkey; MAX_SIGNERS],
}

impl Multisig {
    const LEN: usize = 99;

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
            *slot = Pubkey::new(data[start..start + 32].try_into().unwrap());
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
}
