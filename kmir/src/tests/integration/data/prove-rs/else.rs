fn ite(flag: bool) {
    if flag {
        assert!(false)
    } else {
        assert!(true)
    }
}

fn main() {
    ite(false)
}