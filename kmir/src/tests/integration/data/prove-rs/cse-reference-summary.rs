fn read_nested_ref(x: &&u32) -> u32 {
    **x
}

fn write_nested_ref(x: &mut u32) -> u32 {
    *x = 7;
    *x
}

struct Leaf {
    value: u32,
}

struct Wrapper<'a> {
    leaf: &'a mut Leaf,
    tag: u32,
}

struct Pair {
    a: u32,
    b: u32,
}

fn write_struct_ref(x: &mut Wrapper<'_>) -> u32 {
    x.leaf.value = 11;
    x.tag = 12;
    x.leaf.value + x.tag
}

fn write_pair_fields(a: &mut u32, b: &mut u32) -> u32 {
    *a = 21;
    *b = 22;
    *a + *b
}

fn write_tuple_ref(x: (&mut u32,)) -> u32 {
    *x.0 = 31;
    *x.0
}

fn write_ptr(x: *mut u32) -> u32 {
    unsafe {
        *x = 13;
        *x
    }
}

#[no_mangle]
pub fn caller(x: u32) {
    let first = &x;
    let second = &first;
    let result = read_nested_ref(second);

    assert!(result == x);
}

#[no_mangle]
pub fn mutable_caller(mut x: u32) {
    let result = write_nested_ref(&mut x);

    assert!(x == 7);
    assert!(result == 7);
}

#[no_mangle]
pub fn nested_struct_caller(x: u32) {
    let mut leaf = Leaf { value: x };
    let mut wrapper = Wrapper {
        leaf: &mut leaf,
        tag: 0,
    };
    let result = write_struct_ref(&mut wrapper);

    assert!(wrapper.leaf.value == 11);
    assert!(wrapper.tag == 12);
    assert!(result == 23);
}

#[no_mangle]
pub fn pair_fields_caller(x: u32) {
    let mut pair = Pair { a: x, b: 0 };
    let result = write_pair_fields(&mut pair.a, &mut pair.b);

    assert!(pair.a == 21);
    assert!(pair.b == 22);
    assert!(result == 43);
}

#[no_mangle]
pub fn tuple_ref_caller(mut x: u32) {
    let tuple = (&mut x,);
    let result = write_tuple_ref(tuple);

    assert!(x == 31);
    assert!(result == 31);
}

#[no_mangle]
pub fn ptr_caller(mut x: u32) {
    let result = write_ptr(&mut x as *mut u32);

    assert!(x == 13);
    assert!(result == 13);
}

#[no_mangle]
pub fn projected_caller(x: u32) {
    let first = &x;
    let tuple = (first,);
    let second = &tuple.0;
    let result = read_nested_ref(second);

    assert!(result == x);
}

fn main() {}
