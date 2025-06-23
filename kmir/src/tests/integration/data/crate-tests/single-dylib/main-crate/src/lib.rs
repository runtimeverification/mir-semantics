use std::process::exit;

pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

fn assume(cond: bool) {
    if !cond { exit(0); }
}

// must call test_add_in_range for it to be discovered by linker
pub fn expose_test() {
    testing::test_add_in_range(0, 0);
}



pub mod testing {
    use super::*;

    pub fn test_add_in_range(left: u64, right: u64) {
        let sum = left as u128 + right as u128;
        assume(sum <= u64::MAX as u128);
        let result = add(left, right);

        assert_eq!(result as u128, sum)
    }
}
