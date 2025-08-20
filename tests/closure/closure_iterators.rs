// Test closures with iterators

fn main() {
    let numbers = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    
    // Test 1: map with closure
    let doubled: Vec<i32> = numbers.iter()
        .map(|&x| x * 2)
        .collect();
    
    assert_eq!(doubled, vec![2, 4, 6, 8, 10, 12, 14, 16, 18, 20]);
    
    // Test 2: filter with closure
    let evens: Vec<i32> = numbers.iter()
        .filter(|&&x| x % 2 == 0)
        .cloned()
        .collect();
    
    assert_eq!(evens, vec![2, 4, 6, 8, 10]);
    
    // Test 3: fold with closure
    let sum: i32 = numbers.iter()
        .fold(0, |acc, &x| acc + x);
    
    assert_eq!(sum, 55);
    
    // Test 4: chain multiple iterator operations with closures
    let result: Vec<i32> = numbers.iter()
        .filter(|&&x| x > 5)
        .map(|&x| x * x)
        .collect();
    
    assert_eq!(result, vec![36, 49, 64, 81, 100]);
    
    // Test 5: any and all with closures
    let has_even = numbers.iter().any(|&x| x % 2 == 0);
    let all_positive = numbers.iter().all(|&x| x > 0);
    
    assert!(has_even);
    assert!(all_positive);
    
    // Test 6: find with closure
    let first_divisible_by_3 = numbers.iter().find(|&&x| x % 3 == 0);
    assert_eq!(first_divisible_by_3, Some(&3));
    
    // Test 7: enumerate with closure
    let indexed: Vec<(usize, i32)> = numbers.iter()
        .enumerate()
        .map(|(i, &x)| (i, x * 2))
        .collect();
    
    assert_eq!(indexed[0], (0, 2));
    assert_eq!(indexed[1], (1, 4));
    
    // Test 8: zip with closure
    let letters = vec!['a', 'b', 'c', 'd', 'e'];
    let combined: Vec<String> = numbers.iter()
        .zip(letters.iter())
        .map(|(&num, &letter)| format!("{}{}", letter, num))
        .collect();
    
    assert_eq!(combined[0], "a1");
    assert_eq!(combined[1], "b2");
    
    // Test 9: flat_map with closure
    let ranges = vec![1..4, 5..7, 8..11];
    let flattened: Vec<i32> = ranges.iter()
        .flat_map(|range| range.clone())
        .collect();
    
    assert_eq!(flattened, vec![1, 2, 3, 5, 6, 8, 9, 10]);
    
    // Test 10: scan with closure (stateful iterator)
    let running_sum: Vec<i32> = numbers.iter()
        .scan(0, |state, &x| {
            *state += x;
            Some(*state)
        })
        .collect();
    
    assert_eq!(running_sum, vec![1, 3, 6, 10, 15, 21, 28, 36, 45, 55]);
}
