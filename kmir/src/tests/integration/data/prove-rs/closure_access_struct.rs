struct MyStruct {
    data: i32
}

fn main() {
    // List of MyStruct instances
    let struct_list = [
        MyStruct { data: 10 },
        MyStruct { data: 20 },
        MyStruct { data: 30 },
        MyStruct { data: 40 },
        MyStruct { data: 50 }
    ];
    
    // Closure function that takes &MyStruct reference
    let get_value = |struct_ref: &MyStruct| {
        struct_ref.data
    };
    
    // Use list call style, passing reference
    let result = get_value(&struct_list[2]);
    
    // Verify result
    assert_eq!(result, 30);
}