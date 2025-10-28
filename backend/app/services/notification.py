# Service qui permettrait la logique de la detection des mesures dépassant les seuils prédéfinis.
# et lorsque des capteurs se déconnectent.

from enum import Enum
import app.monitoring.resssources.critical_thresholds as critical_thresholds

class NotificationService:
    def __init__(self):
        self.ranges = {
            "temperature": critical_thresholds.TEMPERATURE_RANGES,
            "ecs": critical_thresholds.ECS_RANGES,
            "ph": critical_thresholds.PH_RANGES,
            "humidity": critical_thresholds.HUMIDITY_RANGES,
        }
    
    
    def check_measure(self, value: float, name: str) -> str | None:
        if name not in self.ranges:
            return f"Unknown sensor: {name}"
        
        warn_limits = self.ranges[name]['warn']
        good_limits = self.ranges[name]['good']

        if value < warn_limits['min'] or value > warn_limits['max']:
            return f"CRITICAL out of range: {name.capitalize()} {value}"
        elif value < good_limits['min'] or value > good_limits['max']:
            return f"WARNING: {name.capitalize()} {value}"
        else:
            return None

