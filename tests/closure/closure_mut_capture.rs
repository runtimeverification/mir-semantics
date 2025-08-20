fn main() {
    let mut counter = 0;
    let numbers = [10, 20, 30];
    
    // Closure with mutable capture
    let mut increment_and_get = |x: i32| {
        counter += 1;
        x + counter
    };
    
    let result1 = increment_and_get(numbers[0]);
    let result2 = increment_and_get(numbers[1]);
    
    assert_eq!(result1, 11); // 10 + 1
    assert_eq!(result2, 22); // 20 + 2
    assert_eq!(counter, 2);
}