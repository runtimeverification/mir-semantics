fn addr_of(ptr: *const i32) -> usize {
    ptr as usize
}

fn main() {
    let x = 7;
    let ptr = &x as *const i32;

    let caller_addr = ptr as usize;
    let callee_addr = addr_of(ptr);

    assert_eq!(caller_addr, callee_addr);
}
