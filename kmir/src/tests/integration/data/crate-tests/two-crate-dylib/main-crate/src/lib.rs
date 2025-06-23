use crate1;
use crate1::MyStruct;

pub fn expose_tests() {
    let result = test_crate1_with(0);

    if let crate1::MyEnum::Bar(result2) = use_unwrap_enum(Some(crate1::MyEnum::Bar(42))) {
        assert_eq!(result.int_field, result2);
    }
}

pub fn test_crate1_with(i: isize) -> MyStruct {
    MyStruct::new(i, Some(crate1::MyEnum::Bar(i)))
}

fn use_unwrap_enum(e: Option<crate1::MyEnum>) -> crate1::MyEnum {
    e.unwrap_or(crate1::MyEnum::Bar(0))
}
