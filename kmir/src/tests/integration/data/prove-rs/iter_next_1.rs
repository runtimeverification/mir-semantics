struct Thing { payload: u16 }

fn main() {
    let a = [Thing{payload: 1}, Thing{payload: 2}, Thing{payload: 3}];

    let mut i = a.iter();
    let elem = i.next();
    assert!(elem.unwrap().payload == 1);
    let elem = i.next();
    assert!(elem.unwrap().payload == 2);
    let elem = i.next();
    assert!(elem.unwrap().payload == 3);
    // let elem = i.next();
    // assert!(elem.is_none());
}