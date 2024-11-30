'''Copyright 2010 DFRobot Co.Ltd
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.'''

import serial
import sys
import os
import time
import requests
from constants import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

'''Beginning class declaration'''
class Ultrasound_Sensor:

  ## Board status 
  STA_OK = 0x00
  STA_ERR_CHECKSUM = 0x01
  STA_ERR_SERIAL = 0x02
  STA_ERR_CHECK_OUT_LIMIT = 0x03
  STA_ERR_CHECK_LOW_LIMIT = 0x04
  STA_ERR_DATA = 0x05

  ## last operate status, users can use this variable to determine the result of a function call. 
  last_operate_status = STA_OK

  ## variable 
  distance = 0

  ## Maximum range
  distance_max = 4500 #A determiner selon les parametres du system
  distance_min = 0
  range_max = 4500

  def __init__(self):
    '''
      @brief    Sensor initialization.
    '''
    self._ser = serial.Serial("/dev/ttyS1", 9600) #Le port est changé pour le microprocesseur
    if self._ser.isOpen() != True:
      self.last_operate_status = self.STA_ERR_SERIAL

  def set_dis_range(self, min, max):
    self.distance_max = max
    self.distance_min = min

  def getDistance(self):
    '''
      @brief    Get measured distance
      @return    measured distance
    '''
    self._measure()
    return self.distance
  
  def _check_sum(self, l):
    return (l[0] + l[1] + l[2])&0x00ff

  def _measure(self):
    data = [0]*4
    i = 0
    timenow = time.time()

    while (self._ser.inWaiting() < 4):
      time.sleep(0.01)
      if ((time.time() - timenow) > 1):
        break
    
    rlt = self._ser.read(self._ser.inWaiting())
    #print(rlt)
    
    index = len(rlt)
    if(len(rlt) >= 4):
      index = len(rlt) - 4
      while True:
        try:
          data[0] = ord(rlt[index])
        except:
          data[0] = rlt[index]
        if(data[0] == 0xFF):
          break
        elif (index > 0):
          index = index - 1
        else:
          break
      #print(data)
      if (data[0] == 0xFF):
        try:
            data[1] = ord(rlt[index + 1])
            data[2] = ord(rlt[index + 2])
            data[3] = ord(rlt[index + 3])
        except:
            data[1] = rlt[index + 1]
            data[2] = rlt[index + 2]
            data[3] = rlt[index + 3]
        i = 4
    #print(data)
    if i == 4:
      sum = self._check_sum(data)
      if sum != data[3]:
        self.last_operate_status = self.STA_ERR_CHECKSUM
      else:
        self.distance = data[1]*256 + data[2]
        self.last_operate_status = self.STA_OK
      if self.distance > self.distance_max:
        self.last_operate_status = self.STA_ERR_CHECK_OUT_LIMIT
        self.distance = self.distance_max
      elif self.distance < self.distance_min:
        self.last_operate_status = self.STA_ERR_CHECK_LOW_LIMIT
        self.distance = self.distance_min
    else:
      self.last_operate_status = self.STA_ERR_DATA
    return self.distance
  
  def DistanceToPercentage(self, SensedDistance, CurrentMinValue, CurrentMaxValue):
    return (SensedDistance - CurrentMinValue) / (CurrentMaxValue - CurrentMinValue)
  
  #CurrentMinValue = minimum water level
  #CurrentMaxValue = maximum water level

'''End class declaration'''

sensor = Ultrasound_Sensor()

def print_distance(distance):
  if sensor.last_operate_status == sensor.STA_OK:
    print("Distance %d mm" %distance)
  elif sensor.last_operate_status == sensor.STA_ERR_CHECKSUM:
    print("ERROR")
  elif sensor.last_operate_status == sensor.STA_ERR_SERIAL:
    print("Serial open failed!")
  elif sensor.last_operate_status == sensor.STA_ERR_CHECK_OUT_LIMIT:
    print("Above the upper limit: %d" %distance)
  elif sensor.last_operate_status == sensor.STA_ERR_CHECK_LOW_LIMIT:
    print("Below the lower limit: %d" %distance)
  elif sensor.last_operate_status == sensor.STA_ERR_DATA:
    print("No data!")


if __name__ == "__main__":
  #Minimum ranging threshold for sensor
  dis_min = 0
  #Highest ranging threshold for sensor
  dis_max = 4500
  sensor.set_dis_range(dis_min, dis_max)
  distance = sensor.getDistance()
  pourcentage = sensor.DistanceToPercentage(distance, DISTANCE_RESERVOIR_VIDE, DISTANCE_RESERVOIR_REMPLI)
  requests.post(f'{SERVER_URL}/water_level', json={"value":pourcentage})
  #Delay time < 0.6s
  #time.sleep(0.3) 