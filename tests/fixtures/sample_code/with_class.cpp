// C++ file with class and methods

#include <iostream>

/**
 * A simple calculator class
 */
class Calculator {
private:
    int result;

public:
    /**
     * Constructor
     */
    Calculator() : result(0) {}

    /**
     * Add two numbers
     */
    int add(int x, int y) {
        result = x + y;
        return result;
    }

    /**
     * Multiply two numbers
     */
    static int multiply(int x, int y) {
        // Calculate the product
        return x * y;
    }

    /**
     * Reset the calculator
     */
    void reset() {
        result = 0;
    }
};

/**
 * A namespace function
 */
namespace Helper {
    int standaloneFunction() {
        return 42;
    }
}
