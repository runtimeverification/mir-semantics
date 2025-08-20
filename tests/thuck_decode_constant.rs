fn main() {
    // Create a struct
    let my_struct = MyStruct { value: 42 };
    
    // Create a reference
    let ref_to_struct = &my_struct;
    
    // This operation will generate the MIR statement you described:
    // Dereference ref_to_struct, then access the .value field
    let result = (*ref_to_struct).value;
    
    assert_eq!(result, 42);
}

struct MyStruct {
    value: i32,
}
