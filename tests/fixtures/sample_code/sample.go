// Sample Go file for testing

package main

import "fmt"

// Greet greets a person by name
func Greet(name string) string {
	return fmt.Sprintf("Hello, %s!", name)
}

// Add adds two numbers
func Add(a, b int) int {
	return a + b
}

func noArgs() {
	fmt.Println("No arguments")
}
