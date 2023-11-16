fn sum_to_n_rec(n:u32) -> u32 {
    match n {
        0 => 0,
        _ => n + sum_to_n_rec(n - 1),
    }
}

fn main() {
    let ans = sum_to_n_rec(10);

    assert!(ans == 55);
}