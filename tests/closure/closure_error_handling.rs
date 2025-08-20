// Test closure error handling

fn main() {
    // Test 1: Closure with Result handling
    let safe_divide = |a: i32, b: i32| -> Result<i32, String> {
        if b == 0 {
            Err("Division by zero".to_string())
        } else {
            Ok(a / b)
        }
    };
    
    let result1 = safe_divide(10, 2);
    let result2 = safe_divide(10, 0);
    
    assert_eq!(result1, Ok(5));
    assert_eq!(result2, Err("Division by zero".to_string()));
    
    // Test 2: Closure with Option handling
    let safe_get = |index: usize, data: &[i32]| -> Option<i32> {
        data.get(index).copied()
    };
    
    let numbers = vec![1, 2, 3, 4, 5];
    let valid_result = safe_get(2, &numbers);
    let invalid_result = safe_get(10, &numbers);
    
    assert_eq!(valid_result, Some(3));
    assert_eq!(invalid_result, None);
    
    // Test 3: Closure with map_err for error transformation
    let parse_number = |s: &str| -> Result<i32, String> {
        s.parse::<i32>()
            .map_err(|e| format!("Failed to parse '{}': {}", s, e))
    };
    
    let parse_result1 = parse_number("123");
    let parse_result2 = parse_number("abc");
    
    assert_eq!(parse_result1, Ok(123));
    assert!(parse_result2.is_err());
    
    // Test 4: Closure with unwrap_or for default values
    let get_with_default = |index: usize, data: &[i32], default: i32| -> i32 {
        data.get(index).copied().unwrap_or(default)
    };
    
    let result3 = get_with_default(1, &numbers, -1);
    let result4 = get_with_default(10, &numbers, -1);
    
    assert_eq!(result3, 2);
    assert_eq!(result4, -1);
    
    // Test 5: Closure with and_then for chaining operations
    let process_data = |input: &str| -> Result<i32, String> {
        input
            .parse::<i32>()
            .map_err(|_| "Parse error".to_string())
            .and_then(|n| {
                if n > 0 {
                    Ok(n * 2)
                } else {
                    Err("Number must be positive".to_string())
                }
            })
    };
    
    let chain_result1 = process_data("5");
    let chain_result2 = process_data("-1");
    let chain_result3 = process_data("abc");
    
    assert_eq!(chain_result1, Ok(10));
    assert_eq!(chain_result2, Err("Number must be positive".to_string()));
    assert_eq!(chain_result3, Err("Parse error".to_string()));
    
    // Test 6: Closure with panic handling (demonstrates what NOT to do)
    let dangerous_divide = |a: i32, b: i32| -> i32 {
        if b == 0 {
            panic!("Division by zero!");
        }
        a / b
    };
    
    // This would panic: dangerous_divide(10, 0);
    // Instead, we test the safe case
    let safe_result = dangerous_divide(10, 2);
    assert_eq!(safe_result, 5);
    
    // Test 7: Closure with custom error types
    #[derive(Debug, PartialEq)]
    enum MathError {
        DivisionByZero,
        Overflow,
    }
    
    let math_divide = |a: i32, b: i32| -> Result<i32, MathError> {
        if b == 0 {
            Err(MathError::DivisionByZero)
        } else if a == i32::MIN && b == -1 {
            Err(MathError::Overflow)
        } else {
            Ok(a / b)
        }
    };
    
    let math_result1 = math_divide(10, 2);
    let math_result2 = math_divide(10, 0);
    
    assert_eq!(math_result1, Ok(5));
    assert_eq!(math_result2, Err(MathError::DivisionByZero));
}
