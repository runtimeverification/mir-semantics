trait Summary {
    fn summarise(&self) -> String;
}

#[allow(dead_code)]
struct Container {
    number: u32,
}

impl Summary for Container {
    fn summarise(&self) -> String {
        "The number is zero or more!".to_string()
    }
}

fn main() {
    let con = Container { number:42 };
    assert!(con.summarise() == "The number is zero or more!");
}