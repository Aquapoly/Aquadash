#!/usr/bin/python3
# SPDX-FileCopyrightText: Copyright (c) 2020 Bryan Siepert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time
import board
import adafruit_shtc3
import requests
import logging
import sys
from constants import *

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 
logging.basicConfig(format = log_format, level = logging.DEBUG)

logger = logging.getLogger()

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
sht = adafruit_shtc3.SHTC3(i2c)

def get_temperature_humidity():
    temperature, relative_humidity = sht.measurements
    values = dict()
    values['temperature'] = temperature
    values['humidity'] = relative_humidity
    return values

if __name__ == '__main__':
    logging.info('Getting temperature and humidity')
    values = get_temperature_humidity();
    requests.post(f'{SERVER_URL}/temperature', json={"value":values['temperature']})
    requests.post(f'{SERVER_URL}/humidity', json={"value":values['humidity']})
