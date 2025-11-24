// Rust file with struct and impl

struct Calculator {
    result: i32,
}

impl Calculator {
    /// Create a new calculator
    fn new() -> Self {
        Calculator { result: 0 }
    }

    /// Add two numbers
    fn add(&mut self, x: i32, y: i32) -> i32 {
        self.result = x + y;
        self.result
    }

    /// Multiply two numbers
    pub fn multiply(&self, x: i32, y: i32) -> i32 {
        // Calculate the product
        x * y
    }
}

/// A standalone function
fn standalone_function() -> i32 {
    42
}
