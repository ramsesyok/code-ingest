"""Python file with various argument types"""


def no_args():
    """Function with no arguments"""
    return None


def with_args(a, b, c):
    """Function with positional arguments"""
    return a + b + c


def with_defaults(x=10, y=20):
    """Function with default arguments"""
    return x + y


def with_type_hints(name: str, age: int) -> str:
    """Function with type hints"""
    return f"{name} is {age} years old"
