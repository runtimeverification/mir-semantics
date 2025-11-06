//! Minimal dual-AccountInfo harness for MIR semantics tests.

use std::cell::{Ref, RefCell, RefMut};

trait MiniPack: Copy {
    const LEN: usize;
    fn pack_into_slice(self, dst: &mut [u8]);
    fn unpack_unchecked(src: &[u8]) -> Self
    where
        Self: Sized;
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct MiniMint {
    decimals: u8,
    supply: u64,
}

impl MiniPack for MiniMint {
    const LEN: usize = 9;

    fn pack_into_slice(self, dst: &mut [u8]) {
        assert_eq!(dst.len(), Self::LEN);
        dst[0] = self.decimals;
        dst[1..].copy_from_slice(&self.supply.to_le_bytes());
    }

    fn unpack_unchecked(src: &[u8]) -> Self {
        let mut supply = [0_u8; 8];
        supply.copy_from_slice(&src[1..]);
        Self {
            decimals: src[0],
            supply: u64::from_le_bytes(supply),
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct MiniTokenAccount {
    owner: [u8; 8],
    amount: u64,
    status: u8,
}

impl MiniPack for MiniTokenAccount {
    const LEN: usize = 17;

    fn pack_into_slice(self, dst: &mut [u8]) {
        assert_eq!(dst.len(), Self::LEN);
        dst[0..8].copy_from_slice(&self.owner);
        dst[8..16].copy_from_slice(&self.amount.to_le_bytes());
        dst[16] = self.status;
    }

    fn unpack_unchecked(src: &[u8]) -> Self {
        let mut owner = [0_u8; 8];
        owner.copy_from_slice(&src[0..8]);
        let mut amount = [0_u8; 8];
        amount.copy_from_slice(&src[8..16]);
        Self {
            owner,
            amount: u64::from_le_bytes(amount),
            status: src[16],
        }
    }
}

pub struct AccountInfo<'a> {
    data: RefCell<&'a mut [u8]>,
}

impl<'a> AccountInfo<'a> {
    pub fn new(data: &'a mut [u8]) -> Self {
        Self {
            data: RefCell::new(data),
        }
    }

    pub fn borrow_data(&self) -> Ref<'_, [u8]> {
        Ref::map(self.data.borrow(), |slice| &**slice)
    }

    pub fn borrow_mut_data(&self) -> RefMut<'_, [u8]> {
        RefMut::map(self.data.borrow_mut(), |slice| &mut **slice)
    }
}

#[no_mangle]
pub fn dual_account_demo(account_info: &AccountInfo, mint_info: &AccountInfo) -> bool {
    let account_read = account_info.borrow_data();
    let mint_read = mint_info.borrow_data();
    let _ = MiniTokenAccount::unpack_unchecked(&account_read);
    let _ = MiniMint::unpack_unchecked(&mint_read);
    drop(account_read);
    drop(mint_read);

    let mut account_write = account_info.borrow_mut_data();
    let mut mint_write = mint_info.borrow_mut_data();
    let expected_account = MiniTokenAccount {
        owner: *b"demoacct",
        amount: 123,
        status: 1,
    };
    let expected_mint = MiniMint {
        decimals: 9,
        supply: 500,
    };
    expected_account.pack_into_slice(&mut account_write);
    expected_mint.pack_into_slice(&mut mint_write);
    drop(account_write);
    drop(mint_write);

    let account_read_after = account_info.borrow_data();
    let mint_read_after = mint_info.borrow_data();
    assert_eq!(
        MiniTokenAccount::unpack_unchecked(&account_read_after),
        expected_account
    );
    assert_eq!(
        MiniMint::unpack_unchecked(&mint_read_after),
        expected_mint
    );

    true
}

fn main() {
    let mut account_bytes = [0_u8; MiniTokenAccount::LEN];
    let mut mint_bytes = [0_u8; MiniMint::LEN];
    let account = AccountInfo::new(&mut account_bytes);
    let mint = AccountInfo::new(&mut mint_bytes);
    let result = dual_account_demo(&account, &mint);
    assert!(result);
}
