use crate1;
use crate1::MyStruct;

fn main() {
    let result = test_crate1_with(Some(42));

    if let crate1::MyEnum::Bar(result2) = use_unwrap_enum(Some(crate1::MyEnum::Bar(42))) {
        assert_eq!(result.int_field, result2);
    }
}

fn test_crate1_with(maybe_i: Option<isize>) -> MyStruct {
    // let (the_i, the_e) = if let Some(i) = maybe_i {
    //     (i, Some(crate1::MyEnum::Bar(i)))
    // } else {
    //     (0, None)
    // };
    let the_i = maybe_i.unwrap_or(0 + 1 + 2 + 3);
    let the_e = maybe_i.map(|i| crate1::MyEnum::Bar(i));

    MyStruct::new(the_i, the_e)
}

fn use_unwrap_enum(e: Option<crate1::MyEnum>) -> crate1::MyEnum {
    e.unwrap_or(crate1::MyEnum::Bar(0))
}
