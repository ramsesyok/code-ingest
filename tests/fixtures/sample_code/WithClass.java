// Java file with class and methods

package com.example;

/**
 * A simple calculator
 */
public class Calculator {
    private int result;

    /**
     * Create a new calculator
     */
    public Calculator() {
        this.result = 0;
    }

    /**
     * Add two numbers
     */
    public int add(int x, int y) {
        this.result = x + y;
        return this.result;
    }

    /**
     * Multiply two numbers
     */
    public static int multiply(int x, int y) {
        // Calculate the product
        return x * y;
    }

    /**
     * A private helper method
     */
    private void reset() {
        this.result = 0;
    }
}

/**
 * A standalone function outside the class
 */
class Helper {
    static int standaloneFunction() {
        return 42;
    }
}
