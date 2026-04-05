fn callee(flag: bool, other: bool) -> bool {
    if flag {
        other
    } else {
        false
    }
}

fn caller(flag: bool, other: bool) {
    let first = callee(flag, other);
    let second = callee(flag, other);
    if first && second {
        assert!(flag);
        assert!(other);
    } else {
        assert!(!flag || !other);
    }
}

fn main() {
    caller(true, true);
}
