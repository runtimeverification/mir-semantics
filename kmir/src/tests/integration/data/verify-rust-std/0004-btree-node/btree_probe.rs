use std::collections::BTreeMap;

fn main() {
    let map: BTreeMap<i32, i32> = BTreeMap::new();
    assert!(map.is_empty());
}
