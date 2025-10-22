struct Foo {
    arr: [u16; 3],
}

fn main() {
    let mut foo = Foo { arr: [11, 22, 33] };
    let subslice = &mut foo.arr[1..];
    subslice[0] = 44;
    assert!(foo.arr == [11, 44, 33]);
}