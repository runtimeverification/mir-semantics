fn get_len(data: &[u8]) -> usize {
    data.len()
}

fn check_size(data: &[u8]) -> bool {
    get_len(data) > 0
}

fn main() {
    let buf = [1u8, 2, 3];
    let r = check_size(&buf);
    assert!(r);
}
