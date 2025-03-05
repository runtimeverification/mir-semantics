fn main() {

    // `not`
    let a = 127u8 + 128u8;     // 255
    let b = !a;                // 0
    let c = !(-123i8);         // 122
    let d = !false;            // true

    // `neg`
    let e = - c;           // -122

// #[allow(arithmetic_overflow)]
//     let f = - ((- 64i8) - 64i8); // -128! (overflow error unless optimising)
// TODO currently fails due to https://github.com/runtimeverification/haskell-backend/pull/4095

    // println!("{a}\n{b}\n{c}\n{d}\n{e}\n{f}\n");
}
