// Subslice projection in a Drop terminator's place.
//
// `let [first, ..] = arr` moves only `first`; the remaining elements
// are dropped in place via Drop(arr.Subslice(1, 3, false)).
// This exercises _projected_ty() resolving the Subslice to the correct
// [Droppable; 2] type so reduce_to() preserves the drop glue.

struct Droppable(u8);

impl Drop for Droppable {
    fn drop(&mut self) {}
}

fn consume(_: Droppable) {}

fn main() {
    let arr = [Droppable(1), Droppable(2), Droppable(3)];
    let [first, ..] = arr;
    consume(first);
}
