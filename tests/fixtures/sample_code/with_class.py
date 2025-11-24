"""Python file with class for testing"""


class Calculator:
    """A simple calculator class"""

    def __init__(self):
        self.result = 0

    def add(self, x, y):
        """Add two numbers"""
        self.result = x + y
        return self.result

    def multiply(self, x, y):
        """Multiply two numbers"""
        # Store the result
        self.result = x * y
        return self.result


def standalone_function():
    """A standalone function"""
    return 42
