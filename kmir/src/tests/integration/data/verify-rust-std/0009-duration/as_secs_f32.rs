use std::time::Duration;

fn test_as_secs_f32_simple() {
    assert!(Duration::from_secs(3).as_secs_f32() == 3.0_f32);
}

fn main() {
    test_as_secs_f32_simple();
}
