use crate1;
use crate1::MyStruct;

pub fn test_crate1_with(i: isize) -> MyStruct {
    MyStruct::new(i, Some(crate1::MyEnum::Bar(i)))
}

fn use_unwrap_enum(e: Option<crate1::MyEnum>) -> crate1::MyEnum {
    e.unwrap_or(crate1::MyEnum::Bar(0))
}
