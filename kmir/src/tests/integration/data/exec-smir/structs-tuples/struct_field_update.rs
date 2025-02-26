struct MyStruct { 
    field0: i32,
    field1: bool,
    field2: f64,
    field3: (i32, i32)
}

fn main() {

    let mut s = MyStruct { field0: 10, field1: false, field2: 10.0, field3: (1, 2) };

    s.field1 = true;
    s.field3.1 = s.field0;
    s.field0 = s.field3.0;
    s.field2 = 42.9;
}