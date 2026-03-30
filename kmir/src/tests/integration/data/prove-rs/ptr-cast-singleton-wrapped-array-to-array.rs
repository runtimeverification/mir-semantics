// W([[T; N]; 1]) -> [T; N] - singleton-array wrapping array (in-wrapper) on source
struct Wrapper([[u8; 2]; 1]);

fn main() {
    let w = Wrapper([[11, 22]]);
    let arr: [u8; 2] = unsafe { *((&w) as *const Wrapper as *const [u8; 2]) };
    assert_eq!(arr, [11, 22]);
}
