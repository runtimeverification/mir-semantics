pub fn add(left: isize, right: isize) -> isize {
    left + right
}

#[derive(Clone, Copy)]
pub struct MyStruct {
    pub int_field: isize,
    pub enum_field: MyEnum,
    pub option_field: Option<MyEnum> 
}

impl MyStruct {
    pub fn new(i: isize, e: Option<MyEnum>) -> Self {
        let enum_field = e.unwrap_or(MyEnum::Foo);
        MyStruct { int_field: add(i, 0), enum_field, option_field: e }
    }
}

#[derive(Clone, Copy)]
pub enum MyEnum {
    Foo,
    Bar(isize)
}

impl MyEnum {
    pub fn default() -> Self { Self::Bar(42) }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
