// [T; N] -> W2(W1([T; N])) - nested struct wrapping on target
#[derive(Clone, Copy, PartialEq, Debug)]
struct Inner([u8; 2]);

#[derive(Clone, Copy, PartialEq, Debug)]
struct Outer(Inner);

fn main() {
    let arr: [u8; 2] = [11, 22];
    let o: Outer = unsafe { *((&arr) as *const [u8; 2] as *const Outer) };
    assert_eq!(o.0 .0, [11, 22]);
}
