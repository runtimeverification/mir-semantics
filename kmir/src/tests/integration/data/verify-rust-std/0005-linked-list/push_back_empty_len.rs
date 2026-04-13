use std::collections::LinkedList;

fn main() {
    let mut list = LinkedList::new();

    assert!(list.is_empty());
    assert_eq!(list.len(), 0);

    list.push_back(10_i32);

    assert!(!list.is_empty());
    assert_eq!(list.len(), 1);
}
