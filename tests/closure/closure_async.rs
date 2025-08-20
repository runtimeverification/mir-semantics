// This example demonstrates async closures
// Note: This requires an async runtime like tokio to actually execute

fn main() {
    let numbers = [1, 2, 3, 4, 5];
    
    // Async closure that captures by value
    let async_process = |index: usize| async move {
        // Simulate async operation (e.g., network request, file I/O)
        std::thread::sleep(std::time::Duration::from_millis(10));
        numbers[index] * 2
    };
    
    // Async closure that captures by reference (requires 'static lifetime)
    let async_process_ref = |index: usize| async move {
        // This would work if numbers had 'static lifetime
        // For demonstration, we'll use a different approach
        index * 2
    };
    
    // Note: To actually run these async closures, you would need:
    // 1. tokio or another async runtime
    // 2. #[tokio::main] attribute on main function
    // 3. .await calls to execute the futures
    
    println!("Async closures defined successfully");
    println!("To execute: use tokio::spawn(async_process(2).await)");
}