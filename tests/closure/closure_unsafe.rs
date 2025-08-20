// Test unsafe closures

fn main() {
    // Test 1: Unsafe closure with raw pointer manipulation
    let data = vec![1, 2, 3, 4, 5];
    let ptr = data.as_ptr();
    
    let unsafe_closure = |index: usize| unsafe {
        *ptr.add(index)
    };
    
    let result = unsafe_closure(2);
    assert_eq!(result, 3);
    
    // Test 2: Unsafe closure with transmute
    let number: u32 = 0x12345678;
    
    let transmute_closure = || unsafe {
        std::mem::transmute::<u32, [u8; 4]>(number)
    };
    
    let bytes = transmute_closure();
    assert_eq!(bytes, [0x78, 0x56, 0x34, 0x12]); // Little-endian
    
    // Test 3: Unsafe closure with static mut
    static mut COUNTER: i32 = 0;
    
    let unsafe_counter = || unsafe {
        COUNTER += 1;
        COUNTER
    };
    
    let count1 = unsafe_counter();
    let count2 = unsafe_counter();
    
    assert_eq!(count1, 1);
    assert_eq!(count2, 2);
    
    // Test 4: Unsafe closure with manual memory management
    let unsafe_alloc = || unsafe {
        let ptr = std::alloc::alloc(
            std::alloc::Layout::from_size_align(4, 4).unwrap()
        );
        if !ptr.is_null() {
            *(ptr as *mut i32) = 42;
            *(ptr as *mut i32)
        } else {
            0
        }
    };
    
    let alloc_result = unsafe_alloc();
    assert_eq!(alloc_result, 42);
    
    // Test 5: Unsafe closure with FFI simulation
    extern "C" {
        fn strlen(s: *const i8) -> usize;
    }
    
    let string = b"hello\0";
    let unsafe_strlen = |s: *const i8| unsafe {
        strlen(s)
    };
    
    let len = unsafe_strlen(string.as_ptr() as *const i8);
    assert_eq!(len, 5);
    
    // Test 6: Unsafe closure with union
    union IntOrFloat {
        i: i32,
        f: f32,
    }
    
    let value = IntOrFloat { i: 42 };
    
    let unsafe_union = || unsafe {
        value.i
    };
    
    let union_result = unsafe_union();
    assert_eq!(union_result, 42);
    
    // Test 7: Unsafe closure with uninitialized memory
    let unsafe_uninit = || unsafe {
        let mut data: [i32; 3] = std::mem::uninitialized();
        data[0] = 1;
        data[1] = 2;
        data[2] = 3;
        data
    };
    
    let uninit_result = unsafe_uninit();
    assert_eq!(uninit_result, [1, 2, 3]);
}
