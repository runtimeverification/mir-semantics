fn callee(flag: bool, other: bool) -> bool {
    if flag {
        other
    } else {
        false
    }
}

fn caller(flag: bool, other: bool) {
    let mut seen_true = false;
    let mut i = 0;
    while i < 2 {
        seen_true = seen_true || callee(flag, other);
        i += 1;
    }

    if seen_true {
        assert!(flag);
        assert!(other);
    } else {
        assert!(!flag || !other);
    }
}

fn main() {
    caller(true, true);
}
