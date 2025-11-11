fn main() {
    checked_add_i32(1,2);
}

/// If the precondition is not met, the program is not executed (exits cleanly, ex falso quodlibet)
macro_rules! precondition {
    ($pre:expr, $block:expr) => {
        if $pre { $block }
    };
}

fn checked_add_i32(a: i32, b: i32) {

    precondition!(
        a.checked_add(b).is_some(),
         unsafe {
            let result = a.unchecked_add(b);
            assert!(result as i64 == a as i64 + b as i64)
        }
    );
}
