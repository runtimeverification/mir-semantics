// Test closure lifetime scenarios

fn main() {
    // Test 1: Closure capturing reference with lifetime
    let data = vec![1, 2, 3, 4, 5];
    
    // This closure captures a reference to data
    let get_value = |index: usize| {
        &data[index]
    };
    
    let result = get_value(2);
    assert_eq!(*result, 3);
    
    // Test 2: Closure returning reference (requires careful lifetime management)
    let numbers = [10, 20, 30, 40, 50];
    
    // This works because numbers lives long enough
    let get_ref = |index: usize| {
        &numbers[index]
    };
    
    let ref_result = get_ref(1);
    assert_eq!(*ref_result, 20);
    
    // Test 3: Closure with explicit lifetime annotation
    fn create_closure<'a>(data: &'a [i32]) -> impl Fn(usize) -> &'a i32 {
        move |index| &data[index]
    }
    
    let test_data = [100, 200, 300];
    let lifetime_closure = create_closure(&test_data);
    let lifetime_result = lifetime_closure(1);
    assert_eq!(*lifetime_result, 200);
    
    // Test 4: Closure that doesn't capture any references
    let no_ref_closure = |x: i32| x * 2;
    let no_ref_result = no_ref_closure(5);
    assert_eq!(no_ref_result, 10);
    
}
