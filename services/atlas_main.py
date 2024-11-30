from .AtlasI2C import (
     AtlasI2C
)
import time
import re
import sys
from .constants import *
import requests

import logging

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 
logging.basicConfig(format = log_format, level = logging.DEBUG)

logger = logging.getLogger()


def get_value(addr) :
    device = AtlasI2C(address=addr, moduletype="EC", name="Patch")
    value = device.query('R')
    to_convert = re.findall(r'\d+(?:\.\d+)?', value)
    return float(to_convert[1])


def main():
     sensor_i2c_addr = -1
     sensor_id = -1
     try:
          sensor_id = sys.argv[1]
          sensor_i2c_addr = SENSOR_ID_TO_I2C_ADDR[sensor_id]
     except IndexError as err:
          logging.error('File must be run with the sensor_id as an argument.')
          return
     except KeyError as err:
          logging.error('Unkonwn sensor type passed as argument (check constants.py).')
          return

     val = get_value(sensor_i2c_addr)
     logging.debug(f"Value read: {val}")
     requests.post(f"{SERVER_URL}/measurements", json={"value":val, "sensor_id": sensor_id})

if __name__ == "__main__":
     main()
