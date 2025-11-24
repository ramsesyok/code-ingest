// Sample Rust file for testing

/// Greet a person
fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

/// Add two numbers
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn no_args() {
    println!("No arguments");
}
