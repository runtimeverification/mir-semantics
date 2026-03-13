#![allow(invalid_reference_casting)]

fn main() {
    let _keep: fn(&AccountInfo<'_>, Pubkey) = repro;
}

#[inline(never)]
#[no_mangle]
pub fn repro(account: &AccountInfo<'_>, replacement: Pubkey) {
    account.assign(replacement);
    assert_eq!(*account.owner, replacement);
}

struct AccountInfo<'a> {
    owner: &'a Pubkey,
}

impl<'a> AccountInfo<'a> {
    #[inline(never)]
    fn assign(&self, new_owner: Pubkey) {
        unsafe {
            std::ptr::write_volatile(
                self.owner as *const Pubkey as *mut [u8; 32],
                new_owner.to_bytes(),
            );
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Pubkey([u8; 32]);

impl Pubkey {
    fn to_bytes(self) -> [u8; 32] {
        self.0
    }
}
