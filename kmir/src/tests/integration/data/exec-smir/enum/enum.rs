#![allow(unused)]
#![allow(dead_code)]
enum Letter {
    A = 65,
    B,
    M = 77,
}

#[repr(u16)]
enum WithData {
    X = 88,
    Y{y:i32} = 89,
    Z{y:i16, z: bool} = 90,
    ZZ(i8, i8, bool) = 9090,
}

fn main() {
    let a = Letter::A;

    let x  = WithData::X;
    let y  = WithData::Y { y: 42};
    let z  = WithData::Z { y:42, z: false };
    let zz = WithData::ZZ(42, 43, true);

    let mut zzz : WithData;

    if let WithData::Y{y} = x {
        let zzz = WithData::Y{y};
    }

    if let Letter::A = a {
        let zzz = a;
    }

    match zz {
        WithData::Y{y:_} => 
            zzz = y,
        WithData::Z{y:_, z} => 
            zzz = WithData::ZZ(0, 0, z),
        _ => 
            zzz = x,
    }

}
