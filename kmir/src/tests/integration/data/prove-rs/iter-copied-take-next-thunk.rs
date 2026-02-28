#[derive(Copy, Clone)]
struct Pubkey([u8; 32]);

fn main() {
    let _keep: fn(usize) -> u8 = repro;
}

#[no_mangle]
pub fn repro(n: usize) -> u8 {
    let keys = [Pubkey([1; 32]); 11];
    let mut it = keys.iter().take(n).copied();

    if 1 <= n && n <= 11 {
        let first = it.next().unwrap();
        first.0[0]
    } else {
        0
    }
}
