use std::collections::BTreeMap;

fn main() {
    let mut map: BTreeMap<i32, i32> = BTreeMap::new();
    map.insert(1_i32, 10_i32);
    map.insert(2_i32, 20_i32);
    assert!(map.len() == 2_usize);
}
