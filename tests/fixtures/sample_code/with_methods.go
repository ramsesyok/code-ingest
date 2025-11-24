// Go file with struct and methods

package main

// Calculator is a simple calculator
type Calculator struct {
	result int
}

// NewCalculator creates a new calculator
func NewCalculator() *Calculator {
	return &Calculator{result: 0}
}

// Add adds two numbers
func (c *Calculator) Add(x, y int) int {
	c.result = x + y
	return c.result
}

// Multiply multiplies two numbers
func (c *Calculator) Multiply(x, y int) int {
	// Calculate the product
	return x * y
}

// StandaloneFunction is a standalone function
func StandaloneFunction() int {
	return 42
}
