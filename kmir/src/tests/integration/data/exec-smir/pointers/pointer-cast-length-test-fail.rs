#![feature(ptr_metadata)]
// example functions asserting lengths of pointer coercions and PtrToPtr casts

fn main() {
    let a = [42; 8];
    array_cast_test(&a);
}

fn array_cast_test(arr: &[u8]) {
    assert!(arr.len() >= 4);
    
    let arr4 = unsafe { *(arr.as_ptr() as *const [u8; 4]) };
    assert!(arr4.len() == 4);
    // println!("Slice of length {l0} converted to array {arr4:?}");

    let arr4_mut = arr.as_ptr() as *mut [u8; 4];
    unsafe {(*arr4_mut)[1] = 41};
    let l4 = unsafe { (*arr4_mut).len() };

    assert!(l4 == 4);
    // println!("Mutated array {arr:?} through {arr4_mut:?} with length {l4}");

    let s4 = &arr4 as &[u8];
    let arr9 = unsafe { *(s4.as_ptr() as *const [u8; 9]) }; // this is undefined behaviour
    assert!(arr9.len() == 9);
    // println!("Produced array of length 9: {arr9:?}");

    // println!("Arrays and addresses:");
    // println!("{:?}: {:?}, length {}", arr.as_ptr(), arr, arr.len());
    // println!("{:?}: {:?}, length {}", arr4.as_ptr(), arr4, arr4.len());
    // println!("{:?}: {:?}, length {}", arr4_mut, unsafe { *arr4_mut }, unsafe { *arr4_mut }.len());
    // println!("{:?}: {:?}, length {}", arr9.as_ptr(), arr9, arr9.len());

}
