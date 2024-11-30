import enum

class SensorType(enum.Enum):
    temperature = "temperature"
    humidity = "humidity"
    ec = "ec"
    ph = "ph"
    water_level = "water_level"
    boolean_water_level = "boolean_water_level"
    oxygen = "oxygen"
