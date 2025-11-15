use std::cell::Cell;

struct Counter {
    value: Cell<i32>,
}

impl Counter {
    fn new(start: i32) -> Self {
        Counter { value: Cell::new(start) }
    }

    fn increment(&self) {
        self.value.set(self.get() + 1);
    }

    fn get(&self) -> i32 {
        self.value.get()
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
