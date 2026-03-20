struct Wrapper([u8; 2]);

fn main() {
    let w = Wrapper([11, 22]);
    let arr: [u8; 2] = unsafe { *((&w) as *const Wrapper as *const [u8; 2]) };
    assert_eq!(arr, [11, 22]);
}
