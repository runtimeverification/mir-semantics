// Test complex capture patterns

fn main() {
    // Test 1: Partial move - some fields moved, others borrowed
    struct Person {
        name: String,
        age: i32,
        scores: Vec<i32>,
    }
    
    let person = Person {
        name: "Alice".to_string(),
        age: 25,
        scores: vec![85, 90, 88],
    };
    
    // Move name and scores, borrow age
    let name_and_scores = move || {
        (person.name, person.scores)
    };
    
    let result = name_and_scores();
    assert_eq!(result.0, "Alice");
    assert_eq!(result.1, vec![85, 90, 88]);
    
    // Test 2: Mixed capture - some by value, some by reference
    let mut counter = 0;
    let data = vec![1, 2, 3, 4, 5];
    
    let mixed_closure = move |index: usize| {
        // data is moved into closure
        // counter is captured by mutable reference
        counter += 1;
        data[index] + counter
    };
    
    // This won't compile because counter is captured by reference
    // but data is moved. Let's fix this:
    
    let mut counter2 = 0;
    let data2 = vec![1, 2, 3, 4, 5];
    
    let mixed_closure2 = |index: usize| {
        counter2 += 1;
        data2[index] + counter2
    };
    
    let result1 = mixed_closure2(2);
    let result2 = mixed_closure2(2);
    
    assert_eq!(result1, 4); // 3 + 1
    assert_eq!(result2, 5); // 3 + 2
    
    // Test 3: Closure capturing different parts of a struct
    struct ComplexData {
        numbers: Vec<i32>,
        metadata: String,
        flag: bool,
    }
    
    let complex = ComplexData {
        numbers: vec![10, 20, 30],
        metadata: "test".to_string(),
        flag: true,
    };
    
    // Capture numbers by value, metadata by reference
    let numbers_closure = move || {
        complex.numbers
    };
    
    let numbers_result = numbers_closure();
    assert_eq!(numbers_result, vec![10, 20, 30]);
    
    // Test 4: Closure with conditional capture
    let condition = true;
    let value1 = vec![1, 2, 3];
    let value2 = vec![4, 5, 6];
    
    let conditional_closure = if condition {
        move || value1
    } else {
        move || value2
    };
    
    let conditional_result = conditional_closure();
    assert_eq!(conditional_result, vec![1, 2, 3]);
    
    // Test 5: Closure capturing enum variants
    enum Data {
        Numbers(Vec<i32>),
        Text(String),
    }
    
    let enum_data = Data::Numbers(vec![1, 2, 3]);
    
    let enum_closure = move || {
        match enum_data {
            Data::Numbers(nums) => nums,
            Data::Text(_) => vec![],
        }
    };
    
    let enum_result = enum_closure();
    assert_eq!(enum_result, vec![1, 2, 3]);
    
    // Test 6: Closure with nested captures
    let outer_data = vec![1, 2, 3];
    let inner_data = vec![4, 5, 6];
    
    let nested_closure = move || {
        let inner_closure = move |index: usize| {
            outer_data[index] + inner_data[index]
        };
        inner_closure(0)
    };
    
    let nested_result = nested_closure();
    assert_eq!(nested_result, 5); // 1 + 4
    
    // Test 7: Closure capturing tuple with mixed ownership
    let tuple_data = (vec![1, 2, 3], "hello".to_string(), 42);
    
    let tuple_closure = move |index: usize| {
        (tuple_data.0[index], tuple_data.1.clone(), tuple_data.2)
    };
    
    let tuple_result = tuple_closure(1);
    assert_eq!(tuple_result, (2, "hello".to_string(), 42));
    
    // Test 8: Closure with reference counting for shared ownership
    use std::rc::Rc;
    
    let shared_data = Rc::new(vec![1, 2, 3, 4, 5]);
    
    let rc_closure1 = {
        let data = Rc::clone(&shared_data);
        move |index: usize| data[index]
    };
    
    let rc_closure2 = {
        let data = Rc::clone(&shared_data);
        move |index: usize| data[index] * 2
    };
    
    let rc_result1 = rc_closure1(2);
    let rc_result2 = rc_closure2(2);
    
    assert_eq!(rc_result1, 3);
    assert_eq!(rc_result2, 6);
}
