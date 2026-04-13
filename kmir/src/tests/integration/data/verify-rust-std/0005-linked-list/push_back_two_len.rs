use std::collections::LinkedList;

fn main() {
    let mut list = LinkedList::new();

    list.push_back(10_i32);
    assert_eq!(list.len(), 1);
    assert!(!list.is_empty());

    list.push_back(20_i32);

    assert_eq!(list.len(), 2);
    assert!(!list.is_empty());
}
