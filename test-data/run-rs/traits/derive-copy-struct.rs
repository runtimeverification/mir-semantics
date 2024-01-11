#[derive(Copy, Clone)]
struct Container {
    number:u32,
}

fn take_first_container(containers: &[Container]) -> Container {
    containers[0]
}

fn main() {
    let con1 = Container { number: 42 };
    let con2 = Container { number: 24 };

    let cons = [con1, con2];

    let first:Container = take_first_container(&cons[..]);

    assert!(first.number == 42);
}