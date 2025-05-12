fn main() {
    let mut prior = 1;
    let x = 10;
    
    // println!("Before: {}", x);
    let _y = &x; // <-- need something else on the stack for the offset to work
    let prior_mut = &mut prior as *mut i32;

    unsafe {
        let prior_alias = prior_mut.add(1);
        *prior_alias = 20;
    }
    
    // println!("After: {}", x);
    assert!(x == 20);
}
