fn classify(x: u32) -> u32 {
    if x > 10 {
        1
    } else {
        0
    }
}

fn main() {
    let a: u32 = 5;
    let result = classify(a);
    assert!(result == 0);
}
