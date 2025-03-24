#[derive(Debug)]
struct MyStruct {
    a_value: i8,
    another: bool,
    a_third: usize,
}

#[derive(Debug)]
struct Enclosing<'a> {
    inner: &'a mut MyStruct
}

fn main () {

    let mut a = MyStruct { a_value: 32, another: false, a_third: 32};

    // mutate field through ref and double-ref
    let r1 = &mut (a.a_value);
    *r1 = 42;
    assert!(a.a_value == 42);
    let mut r1 = &mut (a.a_value);
    let r2 = &mut r1;
    **r2 = 43;
    assert!(a.a_value == 43);

    // create reference-field chain
    let mut e = Enclosing{inner: &mut a};
    let ee = &mut e;

    // read and  write values through chain of ref/field projections
    let vv = (*(*ee).inner).a_value;
    assert!(vv == 43);

    (*(*ee).inner).another = true;

    let r3 = &mut (*ee).inner.a_third;
    *r3 = (*(*ee).inner).a_value as usize;

    assert!(a.another);
    assert!(a.a_third == 43);

}

