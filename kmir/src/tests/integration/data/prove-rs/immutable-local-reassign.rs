fn main() {
    let _ = repro();
}

fn repro() -> usize {
    let mut out = [0usize; 2];
    for i in 0usize..2usize {
        out[i] = i;
    }
    out[1]
}
