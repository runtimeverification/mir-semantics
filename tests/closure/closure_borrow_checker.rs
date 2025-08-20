fn main() {
    let mut data = vec![1, 2, 3, 4, 5];
    
    // Test borrow checker
    let get_value = |index: usize| {
        data[index]
    };
    
    let result = get_value(2);
    assert_eq!(result, 3);
    
    // Can modify data because closure only borrows
    data[2] = 10;
    let new_result = get_value(2);
    assert_eq!(new_result, 10);
}