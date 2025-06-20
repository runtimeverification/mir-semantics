pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

pub mod a_module {
    use super::add;

    pub fn twice(x: u64) -> u64{
        add(x, x)
    }
}

pub fn main() {
    let x = 42;
    assert_eq!(a_module::twice(x), 2 * x);
}