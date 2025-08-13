#[derive(Clone, Copy)]
struct Account {
    balance: u64,
    flags: [u8; 2],
}

#[inline(never)]
fn sink_array_of_struct(p: &&&&&[Account; 1]) -> (u64, u8) {
    let mut bal = 0u64;
    let mut flag = 0u8;
    bal = (*****p)[0].balance;
    flag = (*****p)[0].flags[1];
    (bal, flag)
}

#[inline(never)]
fn from_begin_array_of_struct(begin: &[Account; 1]) -> (u64, u8) {
    let p1 = &begin;
    let p2 = &p1;
    let p3 = &p2;
    let p4 = &p3;
    let p5 = &p4;
    sink_array_of_struct(p5)
}

fn main() {
    let acct = Account { balance: 100, flags: [3, 9] };
    let arr = [acct];
    let (bal, flag) = from_begin_array_of_struct(&arr);
    assert_eq!(bal, 100);
    assert_eq!(flag, 9);
}


