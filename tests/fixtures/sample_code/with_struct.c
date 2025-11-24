// C file with struct and functions

#include <stdlib.h>

/**
 * A simple calculator structure
 */
typedef struct {
    int result;
} Calculator;

/**
 * Create a new calculator
 */
Calculator* create_calculator() {
    Calculator* calc = (Calculator*)malloc(sizeof(Calculator));
    calc->result = 0;
    return calc;
}

/**
 * Add two numbers
 */
int calculator_add(Calculator* calc, int x, int y) {
    calc->result = x + y;
    return calc->result;
}

/**
 * Multiply two numbers
 */
static int multiply(int x, int y) {
    // Calculate the product
    return x * y;
}

// Helper function
void reset(Calculator* calc) {
    calc->result = 0;
}
