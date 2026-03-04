/// Comprehensive test for direct-tag enum decoding.
///
/// Covers:
///   - `#[repr(u8)]` with discriminants 0/1 (baseline, like Option)
///   - `#[repr(u8)]` with discriminants 2/5 (non-zero start)
///   - `#[repr(u16)]` with discriminants 0/256 (wide tag exceeding u8 range)
///   - `#[repr(u8)]` with 3 variants (beyond two-variant restriction)

// --- Baseline: repr(u8), disc 0 / 1 -------------------------------------------

#[repr(u8)]
#[derive(PartialEq)]
enum TwoU8 {
    A(u32) = 0,
    B(u32) = 1,
}

const TWO_U8_A: TwoU8 = TwoU8::A(10);
const TWO_U8_B: TwoU8 = TwoU8::B(20);

// --- Non-zero discriminants: repr(u8), disc 2 / 5 -----------------------------

#[repr(u8)]
#[derive(PartialEq)]
enum NonZero {
    X(u32) = 2,
    Y(u32) = 5,
}

const NZ_X: NonZero = NonZero::X(100);
const NZ_Y: NonZero = NonZero::Y(200);

// --- Wide tag: repr(u16), disc 0 / 256 ----------------------------------------

#[repr(u16)]
#[derive(PartialEq)]
enum WideTag {
    Lo(u32) = 0,
    Hi(u32) = 256,
}

const WIDE_LO: WideTag = WideTag::Lo(42);
const WIDE_HI: WideTag = WideTag::Hi(99);

// --- Three variants: repr(u8), disc 0 / 1 / 2 ---------------------------------

#[repr(u8)]
#[derive(PartialEq)]
enum Three {
    First(u32)  = 0,
    Second(u32) = 1,
    Third(u32)  = 2,
}

const THREE_A: Three = Three::First(1);
const THREE_B: Three = Three::Second(2);
const THREE_C: Three = Three::Third(3);

fn main() {
    // Baseline
    assert!(TWO_U8_A == TwoU8::A(10));
    assert!(TWO_U8_B == TwoU8::B(20));

    // Non-zero discriminants
    assert!(NZ_X == NonZero::X(100));
    assert!(NZ_Y == NonZero::Y(200));

    // Wide tag
    assert!(WIDE_LO == WideTag::Lo(42));
    assert!(WIDE_HI == WideTag::Hi(99));

    // Three variants
    assert!(THREE_A == Three::First(1));
    assert!(THREE_B == Three::Second(2));
    assert!(THREE_C == Three::Third(3));
}
