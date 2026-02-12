import enum

def low_condition(value, condition_value):
    return value < condition_value

def high_condition(value, condition_value):
    return value > condition_value



def always_condition(value, condition_value):
    return True


class ActivationCondition(enum.Enum):
    high = "high"
    low = "low"
    low_or_high = "low_or_high"
    always= "always"

activation_map = {
    ActivationCondition.low: low_condition,
    ActivationCondition.high: high_condition,
    ActivationCondition.always: always_condition,
}