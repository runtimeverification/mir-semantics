use std::cell::UnsafeCell;

fn read(cell: &UnsafeCell<i64>) -> i64 {
    unsafe {
        let raw: *const UnsafeCell<i64> = cell;
        let inner: *const i64 = raw as *const i64;
        *inner
    }
}

fn main() {
    let cell = UnsafeCell::new(41);
    assert!(read(&cell) == 41);
}
