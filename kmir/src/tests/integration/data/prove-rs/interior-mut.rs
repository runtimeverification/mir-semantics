use std::cell::RefCell;

struct Counter {
    value: RefCell<i32>,
}

impl Counter {
    fn new(start: i32) -> Self {
        Counter { value: RefCell::new(start) }
    }

    fn increment(&self) {
        *self.value.borrow_mut() += 1;
    }

    fn get(&self) -> i32 {
        *self.value.borrow()
    }
}

fn main() {
    let counter = Counter::new(0);
    // println!("Before: {}", counter.get());

    // We only have &counter, but can still mutate inside
    counter.increment();
    counter.increment();

    assert!(2 == counter.get());
    // println!("After: {}", counter.get());
}
