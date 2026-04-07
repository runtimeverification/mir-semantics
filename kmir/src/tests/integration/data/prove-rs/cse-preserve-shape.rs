fn callee(flag: bool, other: bool) -> bool {
    if flag {
        other
    } else {
        false
    }
}

fn caller(flag: bool, other: bool) {
    let result = callee(flag, other);
    if result {
        assert!(flag);
        assert!(other);
    } else {
        assert!(!flag || !other);
    }
}

fn main() {
    caller(true, true);
}
