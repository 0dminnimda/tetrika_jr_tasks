import pytest
import sys
from typing import Union
from solution import strict


@strict
def sum_two(a: int, b: int) -> int:
    return a + b

@strict
def process_data(name: str, value: float, active: bool) -> str:
    return f"{name}: {value}" if active else "Inactive"

@strict
def process_user(user: 'User') -> str:
    return user.name

class User:
    def __init__(self, name: str):
        self.name = name

@strict
def update_undefined(x: 'Undefined') -> 'Undefined':
    return x

@strict
def accept_int_or_str_union(data: Union[int, str]) -> str:
    return f"Got {data}"

if sys.version_info >= (3, 10):
    @strict
    def accept_int_or_str_pipe(data: int | str) -> str:
        return f"Got {data}"


def test_correct_types():
    assert sum_two(10, 20) == 30
    assert process_data("test", 3.14, True) == "test: 3.14"

def test_incorrect_int_type_raises_error():
    with pytest.raises(TypeError, match="argument 'b' must be of type 'int', but got 'float'"):
        sum_two(1, 2.0)

def test_incorrect_str_type_raises_error():
    with pytest.raises(TypeError, match="argument 'name' must be of type 'str', but got 'int'"):
        process_data(123, 3.14, True)


def test_forward_reference_annotation_pass():
    user_instance = User("Alice")
    assert process_user(user=user_instance) == "Alice"

def test_forward_reference_annotation_fail():
    with pytest.raises(TypeError, match="argument 'user' must be of type 'User', but got 'str'"):
        process_user(user="not a user object")

def test_undefined_forward_reference():
    with pytest.raises(NameError, match="Cannot resolve type hints for 'update_undefined'. Make sure all forward-referenced types are defined."):
        update_undefined("undefined")


@pytest.mark.skipif(sys.version_info < (3, 10), reason="isinstance(x, Union[...]) requires Python 3.10+")
def test_union_pass():
    assert accept_int_or_str_union(123) == "Got 123"
    assert accept_int_or_str_union("hello") == "Got hello"

@pytest.mark.skipif(sys.version_info < (3, 10), reason="isinstance(x, Union[...]) requires Python 3.10+")
def test_union_fail():
    with pytest.raises(TypeError, match="argument 'data' must be of type .*Union.*int.*str.* but got 'float'"):
        accept_int_or_str_union(123.45)

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Pipe union syntax requires Python 3.10+")
def test_pipe_union_pass():
    assert accept_int_or_str_pipe(123) == "Got 123"
    assert accept_int_or_str_pipe("hello") == "Got hello"

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Pipe union syntax requires Python 3.10+")
def test_pipe_union_fail():
    with pytest.raises(TypeError, match="argument 'data' must be of type .*int.*|.*str.* but got 'float'"):
        accept_int_or_str_pipe(123.45)


if __name__ == "__main__":
    print("Running tests...")
    exit_code = pytest.main(["-v", "-s", __file__])
    print(f"\nTests finished with exit code: {exit_code}")
