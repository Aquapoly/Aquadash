# Service qui permettrait la logique de la detection de quand les mesures dépassent les seuils prédéfinis.
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
    def __init__(self):
        pass
    
    def is_In_Range(value: float, threshold: Thresholds):
        x = Thresholds.threshold.value
        if ((value < x[0]) | (value > x[1])):
            return True
        else:
            return False
