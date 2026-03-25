// W2(W1([T; N])) -> [T; N] - nested struct wrapping on source
struct Inner([u8; 2]);
struct Outer(Inner);

fn main() {
    let o = Outer(Inner([11, 22]));
    let arr: [u8; 2] = unsafe { *((&o) as *const Outer as *const [u8; 2]) };
    assert_eq!(arr, [11, 22]);
}
