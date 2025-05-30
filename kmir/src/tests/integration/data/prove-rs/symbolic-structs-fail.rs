#[allow(dead_code)]
struct IntStruct{
    field1: i16,
    field2: u8,
    field3: bool,
}

#[allow(dead_code)]
struct OtherStruct {
    field1: i16,
    field2: u8,
}

#[allow(dead_code)]
#[allow(unused)]
fn eats_struct_args(
    x1: i16,
    mut x2: IntStruct,
    x3: &OtherStruct,
) -> () {
    if (x2.field1 == (*x3).field1) {
        x2.field2 = (*x3).field2;
        x2.field3 = true;
    } else {
        x2.field1 = x1;
        x2.field3 = false;
    }

    assert!(x2.field3 || x2.field2 != (*x3).field2);
}

fn main () {
    let a = IntStruct{ field1: 0, field2: 1, field3: false};
    let b = OtherStruct{field1: 2, field2: 3};
    eats_struct_args(5, a, &b)
}
