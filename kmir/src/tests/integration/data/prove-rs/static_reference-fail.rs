static NUM: u8 = 55;

fn main() {
    let num_ref = &NUM;
    assert!(*num_ref == 55);
}
