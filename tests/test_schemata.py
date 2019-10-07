import pytest

from src.exceptions import InvalidRequestException
from src.schemata import validate_input


@validate_input({"a": "string"})
def haha(a):
    return 3


def test_validate_input():
    assert haha({"a": "x"}) == 3
    with pytest.raises(InvalidRequestException):
        haha({"a": 4})
    with pytest.raises(InvalidRequestException):
        haha({"a": "x", "b": 5})
    with pytest.raises(InvalidRequestException):
        haha({})
