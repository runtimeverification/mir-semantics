//Oversimplified example from https://github.com/galacticcouncil/HydraDX-node/blob/07f3d0f0755117c4e5abcc3ef2100085d01112b9/math/src/omnipool/math.rs#L52
//The type u256 is not in rust core but implemented in Substrate, sp::core.
// lesson: always used arithmatic functions with overflow handled such as `checked` or `sactuated` versions.
use std::convert::TryFrom;

fn mul1(x:u8, y:u8) -> u8 {
    let _x = x as u16;
    let _y = y as u16;

    let _z = _x * _y;
    let z = u8::try_from(_z).unwrap();
    return z
}

fn mul2(x:u8, y:u8) -> u8 {
    let _x = x as u16;
    let _y = y as u16;

    let _z = _x * _y * 16 / (_y * 4);
    let z = u8::try_from(_z).unwrap();
    return z
}

fn main(){
    //let a = mul1(32, u8::MAX); //should panic
    let b = mul2(32, u8::MAX); // b is expected as 128, but is 63. Overflow eoccured unexpectedly.

    assert_eq!(b, 128)
}