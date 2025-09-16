#[derive(PartialEq, Debug)]
enum Thing<'a> {
    Thing( &'a i16, &'a u16)
}

#[derive(PartialEq, Debug)]
struct Another<'a>(&'a i32, &'a u32);

fn main() {
    assert_eq!(Thing::Thing(&1, &2), Thing::Thing(&1, &2));
    assert_eq!(Another(&1, &2), Another(&1, &2));
    println!("All assertions passed");
}
