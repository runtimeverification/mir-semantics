fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let mut iter = slice.iter().peekable();
    let peeked = iter.peek();

    assert!(peeked == Some(&&1_i32));
}
