// Test closure concurrency and Send/Sync traits

use std::thread;
use std::sync::{Arc, Mutex};

fn main() {
    // Test 1: Closure that implements Send (can be moved to another thread)
    let data = vec![1, 2, 3, 4, 5];
    let send_closure = move |index: usize| {
        data[index] * 2
    };
    
    // This closure can be sent to another thread
    let handle = thread::spawn(move || {
        let result = send_closure(2);
        assert_eq!(result, 6);
    });
    
    handle.join().unwrap();
    
    // Test 2: Closure with Arc for shared state
    let shared_data = Arc::new(Mutex::new(vec![0, 0, 0, 0, 0]));
    let mut handles = vec![];
    
    for i in 0..5 {
        let data_clone = Arc::clone(&shared_data);
        let thread_closure = move || {
            let mut data = data_clone.lock().unwrap();
            data[i] = i as i32 * 2;
        };
        
        let handle = thread::spawn(thread_closure);
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    let final_data = shared_data.lock().unwrap();
    assert_eq!(*final_data, vec![0, 2, 4, 6, 8]);
    
    // Test 3: Closure that captures by value (implements Send)
    let numbers = vec![10, 20, 30, 40, 50];
    let sum_closure = move |start: usize, end: usize| {
        numbers[start..end].iter().sum::<i32>()
    };
    
    let handle1 = thread::spawn(move || {
        let result = sum_closure(0, 2);
        assert_eq!(result, 30); // 10 + 20
    });
    
    handle1.join().unwrap();
    
    // Test 4: Closure with static data (always Send + Sync)
    let static_closure = |x: i32| x * 3;
    
    let handle2 = thread::spawn(move || {
        let result = static_closure(5);
        assert_eq!(result, 15);
    });
    
    handle2.join().unwrap();
    
    // Test 5: Closure that doesn't implement Send (demonstrates what NOT to do)
    let mut local_data = vec![1, 2, 3];
    let non_send_closure = move |index: usize| {
        local_data[index] // This captures local_data by value
    };
    
    // This would work in single-threaded context
    let result = non_send_closure(1);
    assert_eq!(result, 2);
    
    // Test 6: Closure with thread-local storage
    use std::cell::RefCell;
    use std::thread_local;
    
    thread_local! {
        static THREAD_COUNTER: RefCell<i32> = RefCell::new(0);
    }
    
    let thread_local_closure = || {
        THREAD_COUNTER.with(|counter| {
            let mut count = counter.borrow_mut();
            *count += 1;
            *count
        })
    };
    
    let handle3 = thread::spawn(move || {
        let result1 = thread_local_closure();
        let result2 = thread_local_closure();
        assert_eq!(result1, 1);
        assert_eq!(result2, 2);
    });
    
    handle3.join().unwrap();
    
    // Test 7: Closure with atomic operations
    use std::sync::atomic::{AtomicI32, Ordering};
    
    let atomic_counter = Arc::new(AtomicI32::new(0));
    let mut atomic_handles = vec![];
    
    for _ in 0..5 {
        let counter_clone = Arc::clone(&atomic_counter);
        let atomic_closure = move || {
            counter_clone.fetch_add(1, Ordering::SeqCst);
        };
        
        let handle = thread::spawn(atomic_closure);
        atomic_handles.push(handle);
    }
    
    for handle in atomic_handles {
        handle.join().unwrap();
    }
    
    assert_eq!(atomic_counter.load(Ordering::SeqCst), 5);
}
