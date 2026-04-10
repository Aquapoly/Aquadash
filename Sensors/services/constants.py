import os
import dotenv

try:
    ENV_PATH: str = dotenv.find_dotenv(raise_error_if_not_found=True)
except IOError as e:
    print(f"Error: {e}")
    exit(1)
dotenv.load_dotenv(ENV_PATH)

try:
    SERVER_URL = os.environ["SERVER_URL"]
except KeyError:
    print("Error: SERVER_URL not found in environment variables")
    exit(1)

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
    "1": 0x64,  #EC atlas
    "2": 0x63,  #pH atlas
    "3": 0x66   #temp atlas
}

# SENSOR_ID_TO_I2C_ADDR = {
#     "ec": 0x63,
#     "ph": 0x64,
#     "temp": 0x66
# }