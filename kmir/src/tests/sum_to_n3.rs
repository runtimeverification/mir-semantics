fn main () {
    let mut sum = 0;
    let mut i = 0;

    while i <= 5 {
        sum += i;
        i += 1;
    }
    assert!(sum == 15);
}