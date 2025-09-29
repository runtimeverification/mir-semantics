fn main() {
    let multiplier = 5;
    let numbers = [1, 2, 3, 4, 5];
    
    // Closure capturing external variables
    let multiply_by = |x: i32| {
        x * multiplier
    };
    
    let result = multiply_by(numbers[2]);
    assert_eq!(result, 15);
}