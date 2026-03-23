struct Wrapper<T>(T);

fn main() {
    let i = 32_i32;

    unsafe {
        let p_i = &i as *const i32;
        assert!(32 == *p_i);

        let p_w = p_i as *const Wrapper<i32>;
        assert!(32 == (*p_w).0);

        let p_ww = p_w as *const Wrapper<Wrapper<i32>>;
        assert!(32 == (*p_ww).0.0);

        let p_ii = p_ww as *const i32;
        assert!(32 == *p_ii);
    }
}