# Service qui permettrait la logique de la detection des mesures dépassant les seuils prédéfinis.
# et lorsque des capteurs se déconnectent.

from enum import Enum
import app.monitoring.resssources.critical_thresholds
import app.monitoring.prototype

class Thresholds(Enum):
    Temperature = [22, 40]
    Ecs         = [300, 1800]
    Ph          = [5.5, 7]
    Humidity    = [35, 100]


class NotificationService:
    self.ranges = app.monitoring.resssources.critical_thresholds
    def __init__(self):
        self.ranges = {
            "temperature": TEMPERATURE_RANGES,
            "ecs": ECS_RANGES,
            "ph": PH_RANGES,
            "humidity": HUMIDITY_RANGES,
        }
    
    
    def check_measure(self, value: float, name: str) -> str | None:
        if name not in self.ranges:
            return f"Unknown sensor: {name}"
        
        warn_limits = self.ranges[name]['warn']
        good_limits = self.ranges[name]['good']

        if value < warn_limits['min'] or value > warn_limits['max']:
            return f"{name.capitalize()} CRITICAL out of range: {value}"
        elif value < good_limits['min'] or value > good_limits['max']:
            return f"{name.capitalize()} WARNING: {value}"
        else:
            return None
