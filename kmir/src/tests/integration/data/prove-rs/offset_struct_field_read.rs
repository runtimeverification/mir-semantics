struct Foo {
    arr: [u16; 3],
}

fn main() {
    let foo = Foo { arr: [11, 22, 33] };
    let subslice = &foo.arr[1..];
    assert!(subslice == [22, 33]);
}