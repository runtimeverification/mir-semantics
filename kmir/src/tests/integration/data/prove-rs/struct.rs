 struct St {
    a:u32,
    b:u32,
 }

 fn main() {
    let s:St = St { a:1, b:2 };

    assert!(s.a + 1 == s.b);
 }