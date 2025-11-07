fn assign<'a>(dst: &mut &'a i32, src: &&'a i32) {
    *dst = *src;
}

fn main() {
    let x = 1;
    let mut dst = &x;
    let src = dst;

    assign(&mut dst, &src);

    assert_eq!(*dst, 1);
}
