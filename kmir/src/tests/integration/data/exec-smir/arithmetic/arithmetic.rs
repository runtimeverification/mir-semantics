fn main() {

        let a = 127u8 + 128u8;       // 255
    let b = a - 255;             // 0

    let c = 0 - 100i8 - 28i8;    // -128
    let d = c as u8 + 127 - a;   // 0, underflow when reordered

    let e = a as i16 * c as i16; // -32640
    let f = e + c as i16;        // -32768

    // println!("{a}\n{b}\n{c}\n{d}\n{e}\n{f}\n");
}
