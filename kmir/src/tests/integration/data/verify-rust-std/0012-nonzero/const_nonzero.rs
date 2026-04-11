use std::num::NonZeroU8;

// Attempt: use const to pre-compute the NonZero value,
// hoping the compiler constant-folds the transmute away.
const NZ_5: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(5) };
const NZ_3: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(3) };

fn main() {
    test_const_get();
}

fn test_const_get() {
    // If the const is evaluated at compile time, we get a pre-built
    // NonZeroU8 value without runtime transmute.
    let val = NZ_5.get();
    assert!(val == 5);

    let val2 = NZ_3.get();
    assert!(val2 == 3);
}
