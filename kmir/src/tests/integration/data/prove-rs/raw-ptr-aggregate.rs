use std::slice::from_raw_parts;

fn main() {
    let mut arr = [0;3];
    arr[1] = 1;
    arr[2] = 2;
    let arr2 = unsafe { from_raw_parts((&arr).as_ptr(), 2) };
    //let arr2 = unsafe { from_raw_parts((&arr).as_ptr().add(1), 2) };
    assert!(arr2.len() == 2);
    assert!(arr2[0] + 1 == arr[1]);
    assert!(arr2[1] + 1 == arr[2]);
}
