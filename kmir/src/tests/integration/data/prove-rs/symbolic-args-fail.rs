#[allow(dead_code)]
struct MyStruct<'a>{ field: &'a MyEnum}

#[allow(dead_code)]
enum MyEnum {
    My1,
    My2(i8),
}

#[allow(dead_code)]
#[allow(unused)]
fn eats_all_args<'a>(
    x1: i32, 
    x2: &mut u16,
    x3: bool,
    x4: MyStruct<'a>,
    x5: MyEnum,
    x6: &mut [u8],
    x7: &[i8; 3],
    x8: &mut [MyStruct<'a>; 2],
    x9: *const MyStruct<'a>,
) -> () {
    *x2 = x1 as u16;
    if x3 { 
        x8[0] = x4;
    }
    else {
        x8[0] = unsafe { MyStruct{field: (*x9).field} };
    }
    match x5 {
        _ => { 
            if x6.len() > 0
                { x6[0] = x7[0] as u8; }
        }
    }
}

// we need a `main` function that calls eats_all_args
fn main() {
    let e1 = MyEnum::My1;
    let e2 = MyEnum::My2(0);
    let e3 = MyEnum::My1;
    let e4 = MyEnum::My2(0);
    let mut x2 = 0;
    let my1 = MyStruct{field: &e1};
    let my2 = MyStruct{field: &e2};
    let my3 = MyStruct{field: &e3};
    let my4 = MyStruct{field: &MyEnum::My1};
    let mut a1 = [1, 2, 3];
    let a2 = [1, 2, 3];
    eats_all_args(1, &mut x2, true, my1, e4, &mut a1, &a2, &mut [my2, my3], &my4 as *const MyStruct<'_>);

    assert!(false); // makes the test with main fail, as the other one also fails
}
