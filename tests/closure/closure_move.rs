fn main() {
    let data = vec![1, 2, 3, 4, 5];
    
    // Closure with move semantics
    let consume_data = move |index: usize| {
        data[index]
    };
    
    let result = consume_data(2);
    assert_eq!(result, 3);
    
    // Note: data has been moved into the closure and cannot be used here
    // The following line would cause a compilation error:
    // println!("Data: {:?}", data); // Error: use of moved value: `data`
}