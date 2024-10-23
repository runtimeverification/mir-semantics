fn sum_to_n(n:usize) -> usize {
    let mut sum = 0;
    let mut counter = n;

    while counter > 0 {
      sum += counter;
      counter = counter - 1;
    }
    return sum;
}

fn test_sum_to_n() -> () {
    let n = 10;
    let golden = 55;
    let sucess = sum_to_n(n) == golden;
    assert!(sucess);
}


fn main() {
  test_sum_to_n();
  return ();
}
