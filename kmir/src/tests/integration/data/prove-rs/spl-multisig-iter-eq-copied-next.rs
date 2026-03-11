const MAX_SIGNERS: usize = 3;

fn main() {
    let _keep: fn() -> bool = repro;
}

fn account_key(signer: &AccountInfo<'_>) -> Pubkey {
    *signer.key
}

#[inline(never)]
#[no_mangle]
pub fn repro() -> bool {
    let k0 = Pubkey([1; 32]);
    let k1 = Pubkey([2; 32]);
    let k2 = Pubkey([3; 32]);
    let n = 2usize;
    let accounts = [
        AccountInfo { key: &k0 },
        AccountInfo { key: &k1 },
        AccountInfo { key: &k2 },
    ];
    let multisig = Multisig {
        signers: [k1, k2, k0],
    };

    accounts[1..]
        .iter()
        .map(account_key)
        .eq(multisig.signers.iter().take(n).copied())
}

#[derive(Clone)]
struct AccountInfo<'a> {
    key: &'a Pubkey,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Pubkey([u8; 32]);

#[derive(Clone, Debug)]
struct Multisig {
    signers: [Pubkey; MAX_SIGNERS],
}
