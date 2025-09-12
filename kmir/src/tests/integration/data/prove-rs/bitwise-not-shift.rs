fn main() {
    // Integers
    assert!(3_u128 & 7_u128 == 3_u128);
    assert!(3_u128 | 7_u128 == 7_u128);
    assert!(3_u128 ^ 7_u128 == 4_u128);

    // Booleans
    assert!(false | false == false);
    assert!(true | false == true);
    assert!(true & true == true);
    assert!(true & false == false);
    assert!(true ^ true == false);
    assert!(true ^ false == true);

    // Borrows
    assert!(&3 & &7 == 3);
    assert!(&3 | &7 == 7);
    assert!(&3 ^ &7 == 4);
    assert!(&false & &false == false);
    assert!(&true | &true == true);
    assert!(&false ^ &false == false);
}
