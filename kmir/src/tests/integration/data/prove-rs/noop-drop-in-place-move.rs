struct Wrap(u8);

impl Drop for Wrap {
    fn drop(&mut self) {
        // `drop_in_place::<u8>` is compiled as a `NoOpSym`, but moving its pointer
        // argument must still invalidate the current frame's local.
        unsafe { std::ptr::drop_in_place(&mut self.0) };
    }
}

fn main() {
    let _w = Wrap(1);
}
