use std::ops::{Deref, DerefMut};

// A non-Copy payload to avoid CopyForDeref on final value
struct NonCopy(i32);

// Read-only deref chain via Deref (non-Copy wrappers)
#[derive(Clone)]
struct D1<'a> { p: &'a NonCopy }
impl<'a> Deref for D1<'a> {
    type Target = NonCopy;
    fn deref(&self) -> &Self::Target { self.p }
}

#[derive(Clone)]
struct D2<'a> { p: D1<'a> }
impl<'a> Deref for D2<'a> {
    type Target = D1<'a>;
    fn deref(&self) -> &Self::Target { &self.p }
}

#[derive(Clone)]
struct D3<'a> { p: D2<'a> }
impl<'a> Deref for D3<'a> {
    type Target = D2<'a>;
    fn deref(&self) -> &Self::Target { &self.p }
}

#[derive(Clone)]
struct D4<'a> { p: D3<'a> }
impl<'a> Deref for D4<'a> {
    type Target = D3<'a>;
    fn deref(&self) -> &Self::Target { &self.p }
}

// Mutable deref chain via DerefMut (to form an lvalue on LHS)
struct M1<'a> { p: &'a mut NonCopy }
impl<'a> Deref for M1<'a> {
    type Target = NonCopy;
    fn deref(&self) -> &Self::Target { &*self.p }
}
impl<'a> DerefMut for M1<'a> {
    fn deref_mut(&mut self) -> &mut Self::Target { self.p }
}

struct M2<'a> { p: M1<'a> }
impl<'a> Deref for M2<'a> {
    type Target = M1<'a>;
    fn deref(&self) -> &Self::Target { &self.p }
}
impl<'a> DerefMut for M2<'a> {
    fn deref_mut(&mut self) -> &mut Self::Target { &mut self.p }
}

struct M3<'a> { p: M2<'a> }
impl<'a> Deref for M3<'a> {
    type Target = M2<'a>;
    fn deref(&self) -> &Self::Target { &self.p }
}
impl<'a> DerefMut for M3<'a> {
    fn deref_mut(&mut self) -> &mut Self::Target { &mut self.p }
}

// Helper and functions operating on &NonCopy (no CopyForDeref)
fn get(x: &NonCopy) -> i32 { x.0 }
fn id_nc(x: &NonCopy) -> i32 { get(x) }
fn plus_one_nc(x: &NonCopy) -> i32 { get(x) + 1 }
fn sum3_nc(a: &NonCopy, b: &NonCopy, c: &NonCopy) -> i32 { get(a) + get(b) + get(c) }

fn main() {
    let base = NonCopy(42);

    // Build read-only chain (RHS uses Deref, not CopyForDeref along the chain)
    let d1 = D1 { p: &base };
    let d2 = D2 { p: d1.clone() };
    let d3 = D3 { p: d2.clone() };
    let d4 = D4 { p: d3.clone() };

    // Force multiple Deref trait calls explicitly using fully-qualified calls
    let r_ref: &NonCopy = Deref::deref(Deref::deref(Deref::deref(Deref::deref(&d4))));
    let r: i32 = get(r_ref);
    assert!(r == 42);

    // Multiple function calls using the Deref chain explicitly
    let k1 = id_nc(Deref::deref(Deref::deref(Deref::deref(Deref::deref(&d4)))));
    let k2 = plus_one_nc(Deref::deref(Deref::deref(Deref::deref(Deref::deref(&d4)))));
    let k3 = sum3_nc(
        Deref::deref(Deref::deref(Deref::deref(Deref::deref(&d4))))
      , Deref::deref(Deref::deref(Deref::deref(Deref::deref(&d4))))
      , Deref::deref(Deref::deref(Deref::deref(Deref::deref(&d4))))
    );
    assert!(k1 == 42 && k2 == 43 && k3 == 42 + 42 + 42);

    // Build mutable chain for LHS (DerefMut provides lvalue)
    let mut slot = NonCopy(0);
    let m1 = M1 { p: &mut slot };
    let m2 = M2 { p: m1 };
    let mut m3 = M3 { p: m2 };

    // Multi-deref assignment in a single statement via explicit Deref/DerefMut chains
    *DerefMut::deref_mut(
        DerefMut::deref_mut(
            DerefMut::deref_mut(&mut m3)
        )
    ) = NonCopy(get(
        Deref::deref(Deref::deref(Deref::deref(Deref::deref(&d4))))
    ));
    assert!(get(&slot) == 42);

    // More calls after the assignment
    let s = sum3_nc(
        Deref::deref(Deref::deref(Deref::deref(Deref::deref(&d4)))),
        Deref::deref(Deref::deref(Deref::deref(Deref::deref(&d4)))),
        Deref::deref(Deref::deref(Deref::deref(Deref::deref(&d4)))),
    );
    assert!(s == 42 * 3);
}

