extern crate core;

fn main() {
    let values = core::array::from_fn::<i32, 4, _>(|i| i as i32 * 10);

    assert!(values[0] == 0_i32);
    assert!(values[1] == 10_i32);
    assert!(values[2] == 20_i32);
    assert!(values[3] == 30_i32);
}
