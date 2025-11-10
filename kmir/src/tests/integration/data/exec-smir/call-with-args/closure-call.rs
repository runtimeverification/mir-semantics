fn test_t(x: (u32,)) -> u32 { x.0 } // expects a singleton tuple

fn main() {
    let single: u32 = 32;
    let tuple: (u32,) = (single,);

    test_t(tuple); // gets passed a singleton tuple

    let identity = |x| x; // expects a single u32

    identity(single); // gets passed a &closure and a singleton tuple!

    let twice = (single, single);
    let is_equal = |a, b| { assert!(a == b); }; // expects and accesses its arguments as locals _2 and _3 (u32)

    // is_equal(twice); // error
    is_equal(single, single); // gets passed a &closure and a singleton tuple !!!
}
