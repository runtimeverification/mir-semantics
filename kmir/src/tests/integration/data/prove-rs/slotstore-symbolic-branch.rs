fn classify(x: u32) -> u32 {
    if x > 10 {
        1
    } else {
        0
    }
}

fn caller(a: u32) {
    let result = classify(a);
    assert!(result <= 1);
}

fn main() {
    caller(5);
}
