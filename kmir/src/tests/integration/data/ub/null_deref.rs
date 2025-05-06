fn main() {
    let p: *const i32 = std::ptr::null();
    let val:i32;
    unsafe {
        val = *p;
    }
    crash(val);
}

fn crash(_arg: i32) {}
