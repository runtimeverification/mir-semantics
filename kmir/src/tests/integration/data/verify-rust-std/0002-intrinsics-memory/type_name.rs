fn main() {
    // type_name returns a &str with the type's name
    let name_i32 = std::any::type_name::<i32>();
    let name_bool = std::any::type_name::<bool>();

    // The names should be non-empty (avoid string equality which may be complex)
    assert!(name_i32.len() > 0);
    assert!(name_bool.len() > 0);
}
