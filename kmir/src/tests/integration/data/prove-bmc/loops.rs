// Loops for testing `kmir prove --bmc-depth` (bounded model checking).
// Without a bound, the loops on symbolic conditions never terminate symbolically.

/// A loop on a symbolic condition: the proof splits at `i < n` in every iteration.
#[no_mangle]
pub fn count_up(n: u64) -> u64 {
    let mut i = 0;
    while i < n {
        i += 1;
    }
    i
}

/// A loop on a decided condition: it runs to completion without splitting.
#[no_mangle]
pub fn count_fixed() -> u64 {
    let mut i = 0;
    while i < 5 {
        i += 1;
    }
    i
}

/// Two loops in sequence, each on a symbolic condition: each is bounded on its own.
#[no_mangle]
pub fn two_loops(n: u64, m: u64) -> u64 {
    let mut i = 0;
    while i < n {
        i += 1;
    }
    let mut j = 0;
    while j < m {
        j += 1;
    }
    i + j
}

fn main() {
    count_up(3);
    count_fixed();
    two_loops(2, 3);
}
