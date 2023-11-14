fn fibonacci(n:u32) -> u32 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci(n - 2) + fibonacci(n - 1),
    }
}

fn main() {
    let ans = fibonacci(5);

    assert!(ans == 5);
}