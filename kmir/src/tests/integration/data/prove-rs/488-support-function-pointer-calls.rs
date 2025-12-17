use std::convert::TryFrom;
use std::array;

// inspired by solana-pubkey but very simple code
#[allow(dead_code)]
struct EightBytes([u8;8]);

impl From<[u8;8]> for EightBytes {
    fn from(bytes: [u8;8]) -> Self { Self(bytes) } 
}

// causing problems with the extraction
// the `try_from` and `from` from stdlib are not available in the SMIR
impl TryFrom<&[u8]> for EightBytes {
    type Error = array::TryFromSliceError;
    fn try_from(bytes: &[u8]) -> Result<EightBytes, Self::Error> {
        <[u8;8]>::try_from(bytes).map(Self::from) 
    }
}

fn main() {
    let bytes: [u8;8] = [1,2,3,4,5,6,7,8];
    let slice: &[u8] = &bytes;
    let thing: Result<EightBytes, _> = EightBytes::try_from(slice);
    assert!(thing.is_ok());
}
