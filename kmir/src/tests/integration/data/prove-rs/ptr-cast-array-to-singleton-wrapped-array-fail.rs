// [T; N] -> W([[T; N]; 1]) - singleton-array wrapping array (in-wrapper) on target
#[derive(Clone, Copy, PartialEq, Debug)]
struct Wrapper([[u8; 2]; 1]);

fn main() {
    let arr: [u8; 2] = [11, 22];
    let w: Wrapper = unsafe { *((&arr) as *const [u8; 2] as *const Wrapper) };
    assert_eq!(w.0, [[11, 22]]);
}
