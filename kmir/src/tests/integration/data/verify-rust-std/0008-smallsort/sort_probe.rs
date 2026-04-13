use std::cmp::Ord;

fn main() {
    let mut values = [3_i32, 1_i32, 2_i32];
    values.sort_by(Ord::cmp);
    assert!(values == [1_i32, 2_i32, 3_i32]);
}
