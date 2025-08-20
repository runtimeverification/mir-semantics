// Test closure traits: Fn, FnMut, FnOnce

fn main() {
    // Test 1: Fn trait - can be called multiple times, captures by reference
    let numbers = [1, 2, 3, 4, 5];
    let fn_closure = |index: usize| numbers[index];
    
    // Can call multiple times
    assert_eq!(fn_closure(0), 1);
    assert_eq!(fn_closure(1), 2);
    assert_eq!(fn_closure(2), 3);
    
    // Test 2: FnMut trait - can be called multiple times, captures by mutable reference
    let mut counter = 0;
    let mut fnmut_closure = |x: i32| {
        counter += 1;
        x + counter
    };
    
    assert_eq!(fnmut_closure(10), 11); // 10 + 1
    assert_eq!(fnmut_closure(10), 12); // 10 + 2
    assert_eq!(counter, 2);
    
    // Test 3: FnOnce trait - can only be called once, takes ownership
    let data = vec![1, 2, 3];
    let fnonce_closure = move |index: usize| {
        data[index] // data is moved into closure
    };
    
    // Can only call once
    let result = fnonce_closure(1);
    assert_eq!(result, 2);
    
    // Test 4: Trait objects with closures
    let closures: Vec<Box<dyn Fn(i32) -> i32>> = vec![
        Box::new(|x| x * 2),
        Box::new(|x| x + 10),
        Box::new(|x| x * x),
    ];
    
    for (i, closure) in closures.iter().enumerate() {
        let result = closure(5);
        match i {
            0 => assert_eq!(result, 10), // 5 * 2
            1 => assert_eq!(result, 15), // 5 + 10
            2 => assert_eq!(result, 25), // 5 * 5
            _ => unreachable!(),
        }
    }
    
    // Test 5: Generic function with closure trait bounds
    fn apply_operation<F>(f: F, x: i32) -> i32 
    where 
        F: Fn(i32) -> i32 
    {
        f(x)
    }
    
    let add_five = |x| x + 5;
    let result = apply_operation(add_five, 10);
    assert_eq!(result, 15);
    
    // Test 6: Closure that implements multiple traits
    let mut state = 0;
    let multi_trait_closure = |x: i32| {
        state += x;
        state
    };
    
    assert_eq!(multi_trait_closure(5), 5);
    assert_eq!(multi_trait_closure(3), 8);
}
