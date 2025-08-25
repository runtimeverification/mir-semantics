use std::hint::black_box;

fn add_one(x: u32) -> u32 {
    x + 1
}

fn main() {
    let input = 10;

    // We are calling `add_one(input)`, which produces the value 11.
    // Then, we pass this RESULT (11) into black_box.
    let result = black_box(add_one(input));

    // This forces the compiler to actually execute the `add_one` function,
    // because it cannot know what `black_box` will do with the result.
    assert_eq!(result, 11);
}