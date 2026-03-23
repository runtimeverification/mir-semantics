// Reproducer for issue #638: alignment check block gets stuck
// When dereferencing a raw pointer, the compiler inserts an alignment check
// that transmutes the pointer to usize. This transmute has no matching rule.

struct Thing { payload: i16 }

fn main() {
    let a = [Thing { payload: 1 }, Thing { payload: 2 }, Thing { payload: 3 }];
    let p = &a as *const Thing;
    let p1 = unsafe { p.add(1) };

    let two = unsafe { (*p1).payload };
    assert!(two == 2);
}
