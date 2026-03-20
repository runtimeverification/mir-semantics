/// Comprehensive test for direct-tag enum decoding.
///
/// Covers:
///   - `#[repr(u8)]` with discriminants 0/1 (baseline, like Option)
///   - `#[repr(u8)]` with discriminants 2/5 (non-zero start)
///   - `#[repr(u16)]` with discriminants 0/256 (wide tag exceeding u8 range)
///   - `#[repr(u8)]` with 3 variants (beyond two-variant restriction)

// --- Baseline: repr(u8), disc 0 / 1 -------------------------------------------

#[repr(u8)]
enum TwoU8 {
    A(bool) = 0,
    B(bool) = 1,
}

const TWO_U8_A: TwoU8 = TwoU8::A(true);
const TWO_U8_B: TwoU8 = TwoU8::B(false);

// --- Non-zero discriminants: repr(u8), disc 2 / 5 -----------------------------

#[repr(u8)]
enum NonZero {
    X(bool) = 2,
    Y(bool) = 5,
}

const NZ_X: NonZero = NonZero::X(false);
const NZ_Y: NonZero = NonZero::Y(true);

// --- Wide tag: repr(u16), disc 0 / 256 ----------------------------------------

#[repr(u16)]
enum WideTag {
    Lo(bool) = 0,
    Hi(bool) = 256,
}

const WIDE_LO: WideTag = WideTag::Lo(true);
const WIDE_HI: WideTag = WideTag::Hi(false);

// --- Three variants: repr(u8), disc 0 / 1 / 2 ---------------------------------

#[repr(u8)]
enum Three {
    First(bool)  = 0,
    Second(bool) = 1,
    Third(bool)  = 2,
}

const THREE_A: Three = Three::First(true);
const THREE_B: Three = Three::Second(false);
const THREE_C: Three = Three::Third(true);

fn main() {
    // Baseline
    assert!(matches!(TWO_U8_A, TwoU8::A(true)));
    assert!(matches!(TWO_U8_B, TwoU8::B(false)));

    // Non-zero discriminants
    assert!(matches!(NZ_X, NonZero::X(false)));
    assert!(matches!(NZ_Y, NonZero::Y(true)));

    // Wide tag
    assert!(matches!(WIDE_LO, WideTag::Lo(true)));
    assert!(matches!(WIDE_HI, WideTag::Hi(false)));

    // Three variants
    assert!(matches!(THREE_A, Three::First(true)));
    assert!(matches!(THREE_B, Three::Second(false)));
    assert!(matches!(THREE_C, Three::Third(true)));
}
