#[derive(Clone, Copy, PartialEq, Debug)]
struct Wrapper([u8; 2]);

fn main() {
    let arr: [u8; 2] = [11, 22];
    let w: Wrapper = unsafe { *((&arr) as *const [u8; 2] as *const Wrapper) };
    assert_eq!(w.0, [11, 22]);
}
