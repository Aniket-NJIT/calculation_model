import pytest
from app.operations import add, subtract, multiply, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1.5, 2.5) == 1.0

def test_subtract():
    assert subtract(10, 5) == 5
    assert subtract(0, 5) == -5

def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 3) == -6

def test_divide():
    assert divide(10, 2) == 5.0
    with pytest.raises(ValueError, match="Cannot divide by zero!"):
        divide(10, 0)