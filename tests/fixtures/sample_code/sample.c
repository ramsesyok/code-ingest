// Sample C file for testing

#include <stdio.h>

/**
 * Greet a person by name
 */
char* greet(char* name) {
    static char buffer[100];
    sprintf(buffer, "Hello, %s!", name);
    return buffer;
}

/**
 * Add two numbers
 */
int add(int a, int b) {
    return a + b;
}

void no_args() {
    printf("No arguments\n");
}
