struct S {
    field0: i32,
    field1: bool,
    field2: f64
}

fn main() {
    let s = S { field0: 10, field1: false, field2: 10.0 };
    let t = (11, true, s.field2);

    foo(s.field0, s.field1, s.field2);
    foo(t.0, t.1, t.2);
}

fn foo(_i:i32, _b:bool, _f:f64) {

}