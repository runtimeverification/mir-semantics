fn main() {

    let a: u16 = 33023 ; // 2^15 + (2^8 - 1);
    let b = a as i8; // -1
    let c = a as i16; // -32513 = a - 2^16
    let d = a as isize; // 33023

}