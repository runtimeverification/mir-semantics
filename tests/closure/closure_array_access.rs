fn main() {
    // Simple data structure
    let numbers = [10, 20, 30, 40, 50];
    
    // Keep closure function and list call style
    let get_value = |index: usize| {
        numbers[index]
    };
    
    // Use list call style
    let result = get_value(2);
    
    // Verify result
    assert_eq!(result, 30);
}