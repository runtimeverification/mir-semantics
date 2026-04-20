// Reproducer: Subslice projection on an array of Drop types.
//
// `let [first, rest @ ..] = arr` generates a Subslice projection that
// changes the type from [Droppable; 3] to [Droppable; 2]. The SMIR
// linker's _projected_ty() currently returns the original array type
// for Subslice, which could cause drop-glue mis-resolution when
// Subslice projections appear in Drop terminator places.

struct Droppable(u8);

impl Drop for Droppable {
    fn drop(&mut self) {}
}

fn main() {
    let arr = [Droppable(1), Droppable(2), Droppable(3)];
    let [first, rest @ ..] = arr;
    assert!(first.0 == 1);
    assert!(rest[0].0 == 2);
    assert!(rest[1].0 == 3);
}
