fn ite(flag: bool) {
    if flag {
        assert!(true)
    } else {
        assert!(false)
    }
}

fn main() {
    ite(true)
}