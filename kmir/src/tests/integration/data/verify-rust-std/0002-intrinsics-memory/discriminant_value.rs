fn main() {
    let none: Option<i32> = None;
    let some_a = Some(7_i32);
    let some_b = Some(11_i32);

    let none_discriminant = core::mem::discriminant(&none);
    let some_a_discriminant = core::mem::discriminant(&some_a);
    let some_b_discriminant = core::mem::discriminant(&some_b);

    assert!(none_discriminant != some_a_discriminant);
    assert!(some_a_discriminant == some_b_discriminant);
}
