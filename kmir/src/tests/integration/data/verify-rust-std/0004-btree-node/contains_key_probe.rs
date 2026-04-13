use std::collections::BTreeMap;

fn main() {
    let mut map: BTreeMap<i32, i32> = BTreeMap::new();
    map.insert(1_i32, 10_i32);
    assert!(map.contains_key(&1_i32));
    assert!(!map.contains_key(&2_i32));
}
