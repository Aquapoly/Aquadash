import os

# SERVER_URL = os.environ.get('TABLE2_URL')
SERVER_URL = "http://aquapi.local:5000"

# Capteur niveau d'eau ultrason
DISTANCE_RESERVOIR_VIDE = 236
DISTANCE_RESERVOIR_REMPLI = 55

#PIN utilisé pour la pompe
PUMP_PIN = 26

#ETAT DES PIN
OFF = 0
ON = 1

# Sensor IDs
# Majeed est cave, il faut faire un dict qui associe
# i2caddress --> sensor_id (pris de aquadash)
SENSOR_ID_TO_I2C_ADDR = {
    "2": 0x64,  #EC atlas
    "3": 0x63,  #pH atlas
    "4": 0x66   #temp atlas
}

# SENSOR_ID_TO_I2C_ADDR = {
#     "ec": 0x63,
#     "ph": 0x64,
#     "temp": 0x66
# }