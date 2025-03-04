fn main() {

    unsafe {
        let a = 127u8 + 127u8;       // 254
        let b = a.unchecked_add(1);  // 255

        let c = 0 - 100i8;           // -100
        let d = c.unchecked_sub(28);  // -128

        let e = b as i16 * d as i16; // -32640
        let f = e + d as i16;        // -32768

        // println!("{a}\n{b}\n{c}\n{d}\n{e}\n{f}\n");

    }

}