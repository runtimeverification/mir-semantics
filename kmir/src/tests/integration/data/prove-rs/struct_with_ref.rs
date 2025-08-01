struct WithRef<'a> {
    a_ref: &'a AThing,
}

struct AThing {
    a_field: i8,
    another: i16,
}

fn main() {
    let a_thing = AThing{ a_field: 1, another: 2};
    let a_ref = &a_thing;
    let with_ref = WithRef{a_ref};

    assert!(with_ref.a_ref.a_field == 1 && a_thing.another == 2); // works
    f(with_ref);
}

fn f(w: WithRef) {
    assert!(2 * w.a_ref.a_field as i16 == w.a_ref.another);
}