// Test recursive closures

fn main() {
    // Test 1: Recursive closure using a helper function
    fn factorial(n: u32) -> u32 {
        if n <= 1 {
            1
        } else {
            n * factorial(n - 1)
        }
    }
    
    let factorial_closure = |n: u32| factorial(n);
    
    assert_eq!(factorial_closure(5), 120);
    assert_eq!(factorial_closure(0), 1);
    
    // Test 2: Recursive closure using a struct with FnMut
    struct RecursiveClosure {
        func: Option<Box<dyn FnMut(u32) -> u32>>,
    }
    
    let mut fib_closure = RecursiveClosure { func: None };
    fib_closure.func = Some(Box::new(move |n: u32| {
        if n <= 1 {
            n
        } else {
            // This is a simplified version - in practice you'd need more complex setup
            n
        }
    }));
    
    // Test 3: Recursive closure using a fixed-point combinator pattern
    fn fix<F, T>(f: F) -> impl Fn(T) -> T
    where
        F: Fn(&dyn Fn(T) -> T, T) -> T,
    {
        move |x| f(&fix(&f), x)
    }
    
    let factorial_fix = fix(|f, n: u32| {
        if n <= 1 {
            1
        } else {
            n * f(n - 1)
        }
    });
    
    assert_eq!(factorial_fix(5), 120);
    
    // Test 4: Recursive closure with memoization
    use std::collections::HashMap;
    use std::cell::RefCell;
    
    let memo = RefCell::new(HashMap::new());
    let mut fib_memo = |n: u32| -> u32 {
        if let Some(&result) = memo.borrow().get(&n) {
            return result;
        }
        
        let result = if n <= 1 {
            n
        } else {
            fib_memo(n - 1) + fib_memo(n - 2)
        };
        
        memo.borrow_mut().insert(n, result);
        result
    };
    
    assert_eq!(fib_memo(10), 55);
    
    // Test 5: Recursive closure with accumulator
    let sum_range = |start: i32, end: i32| {
        fn helper(acc: i32, current: i32, end: i32) -> i32 {
            if current > end {
                acc
            } else {
                helper(acc + current, current + 1, end)
            }
        }
        helper(0, start, end)
    };
    
    assert_eq!(sum_range(1, 5), 15);
}
