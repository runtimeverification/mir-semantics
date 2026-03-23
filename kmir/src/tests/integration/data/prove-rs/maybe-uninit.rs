use std::mem::MaybeUninit;
fn main() {
    let m_init = MaybeUninit::new(1);
    let init = unsafe { m_init.assume_init() };

    assert!(init == 1);
}
