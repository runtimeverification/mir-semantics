pub fn test(b: bool, x: u8, y: i32) -> () {
    let _x = i32::from(x);
    assert!(_x >= 0);
    if y >= _x {
        assert!(y - _x >= 0);
    } else if y >= 0 {
        assert!(_x - y >= 0);
    } else if b {
        assert!(y < 0);
    } else {
        assert_eq!(b, y >= 0);
    }
}
