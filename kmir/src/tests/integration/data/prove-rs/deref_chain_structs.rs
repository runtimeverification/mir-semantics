struct L1<'a> {
    p: &'a i32,
}

struct L2<'a> {
    p: *const L1<'a>,
}

struct L3<'a> {
    p: &'a L2<'a>,
}

struct M1 {
    p: *mut i32,
}

struct M2<'a> {
    p: &'a mut M1,
}

fn main() {
    // Read-only chain: reference -> raw pointer -> reference -> value
    let a = 42;
    let l1 = L1 { p: &a };
    let l2 = L2 { p: &l1 as *const L1 };
    let l3 = L3 { p: &l2 };

    let v = unsafe {
        let n2: &L2 = l3.p;      // &L2
        let n1: &L1 = &*n2.p;    // *const L1 -> &L1
        *n1.p                    // &i32 -> i32
    };
    assert!(v == 42);

    // Writable chain: mutate through a raw pointer guarded by an outer reference
    let mut b = 0;
    let mut m1 = M1 { p: &mut b as *mut i32 };
    let mut m2 = M2 { p: &mut m1 };
    unsafe {
        *(*m2.p).p = 123;
    }
    assert!(b == 123);
}


