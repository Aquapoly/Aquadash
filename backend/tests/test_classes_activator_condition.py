from app.classes.activation_condition import *
import pytest

# Test low_condition
@pytest.mark.parametrize("value, condition_value, expected", [
    (1,2,True), (1,1,False), (-1,0,True), (-10,-10,False), (float("-inf"),0,True), (0,float("inf"),True)
])
def test_low_condition(value, condition_value, expected):
    """Test the low_condition return type and value"""
    result = low_condition(value, condition_value)

    assert isinstance(result, bool), f"Result shoud be a boolean, was {type(result)}"
    assert result == expected, f"Result shoud be {expected}, was {result}"


# Test high_condition
@pytest.mark.parametrize("value, condition_value, expected", [
    (1,2,False), (1,1,False), (-1,0,False), (-10,-10,False), (float("-inf"),0,False), (0,float("inf"),False)
])
def test_high_condition(value, condition_value, expected):
    """Test the high_condition return type and value"""
    result = high_condition(value, condition_value)

    assert isinstance(result, bool), f"Result shoud be a boolean, was {type(result)}"
    assert result == expected, f"Result shoud be {expected}, was {result}"


# Test always_condition
@pytest.mark.parametrize("value, condition_value, expected", [
    (1,2,True), (1,1,True), (-1,0,True), (-10,-10,True), (float("-inf"),0,True), (0,float("inf"),True)
])
def test_always_condition(value, condition_value, expected):
    """Test the always_condition return type and value"""
    result = always_condition(value, condition_value)

    assert isinstance(result, bool), f"Result shoud be a boolean, was {type(result)}"
    assert result == expected, f"Result shoud be {expected}, was {result}"