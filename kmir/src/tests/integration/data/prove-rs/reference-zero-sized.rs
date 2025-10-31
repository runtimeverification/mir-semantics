struct Marker;

fn main() {
    let m = Marker;
    let r = &m;
    std::mem::drop::<&Marker>(r);
}
