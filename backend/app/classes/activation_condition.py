import enum

def low_condition(value, min, max):
    return value < min

def high_condition(value, min, max):
    return value > max

def low_or_high_condition(value, min, max):
    return value < min or value > max

def always_condition(value, min, max):
    return True


class ActivationCondition(enum.Enum):
    high = "high"
    low = "low"
    low_or_high = "low_or_high"
    always= "always"

activation_map = {
    ActivationCondition.low: low_condition,
    ActivationCondition.high: high_condition,
    ActivationCondition.low_or_high: low_or_high_condition,
    ActivationCondition.always: always_condition,
}