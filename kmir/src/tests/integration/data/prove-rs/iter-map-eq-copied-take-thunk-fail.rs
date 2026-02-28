const TAKE_N: usize = 3;

fn main() {
    let _keep: fn(&[AccountInfo<'_>; 5], [Pubkey; 11]) -> bool = repro;
}

#[no_mangle]
pub fn repro(accounts: &[AccountInfo<'_>; 5], signers: [Pubkey; 11]) -> bool {
    accounts[2..]
        .iter()
        .map(|signer| *signer.key)
        .eq(signers.iter().take(TAKE_N).copied())
}

#[derive(Clone)]
struct AccountInfo<'a> {
    key: &'a Pubkey,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Pubkey([u8; 32]);
