use std::collections::BTreeMap;

fn main() {
    let mut map: BTreeMap<i32, i32> = BTreeMap::new();
    assert!(map.insert(1_i32, 10_i32).is_none());
    assert!(map.insert(1_i32, 20_i32).unwrap() == 10_i32);
}
