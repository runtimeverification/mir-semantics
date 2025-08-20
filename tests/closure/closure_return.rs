fn main() {
    let numbers = [1, 2, 3, 4, 5];
    
    // Function that returns a closure
    fn create_adder(addend: i32) -> impl Fn(i32) -> i32 {
        move |x| x + addend
    }
    
    let add_five = create_adder(5);
    let result = add_five(numbers[2]);
    
    assert_eq!(result, 8); // 3 + 5
}