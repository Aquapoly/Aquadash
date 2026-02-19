#source <https://www.tomshardware.com/how-to/control-raspberry-pi-5-gpio-with-python-3>
import gpiod
import time
import requests
import json
import os
from constants import OFF, ON, SERVER_URL, PUMP_PIN

def get_raspberry_pi_model():
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip()
            return model
    except FileNotFoundError:
        return "Unknown Raspberry Pi model"

class Actuator:
    #period is the time between each check for activation
    def __init__(self,pin,id):
        print("Creating actuator object.")
        self.duration = 0
        self.period = 0
        model = get_raspberry_pi_model()
        print(f"Detected Raspberry Pi model: {model}")
        if "Raspberry Pi 5" in model:
            self.chip = gpiod.Chip('gpiochip4') #valid syntax for pi 5 
        else:
            self.chip = gpiod.Chip('/dev/gpiochip0') #valid syntax for raspberry pi 4
        self.pump_line = self.chip.get_line(pin)
        self.pump_line.request(consumer="PUMP", type=gpiod.LINE_REQ_DIR_OUT)
        self.pump_line.set_value(OFF)
        self.is_connected = True
        self.actuator_id = id
        self.activate = False
        self.stop_pump()

    def start_pump(self):
        self.pump_line.set_value(ON) 

    def stop_pump(self):
        self.pump_line.set_value(OFF)

    def cleanup(self):
        self.pump_line.release()
        self.chip.close()

    def initLoop(self):
        print("Starting actuator loop")
        while(self.is_connected):
            if(self.activate):
                self.start_pump()
                time.sleep(self.duration)
                self.stop_pump()
                requests.patch(f"{SERVER_URL}/actuators/{self.actuator_id}/last_activated", data={})
                self.activate = False
            time.sleep(self.period)
            response = requests.get(f"{SERVER_URL}/actuators/{self.actuator_id}/state")
            if response.status_code == 200:
                data = response.json()
                print(data)
                self.activate, status, self.duration , self.period = data["activate"], data["status"], data["duration"], data["period"]
                print(f"Status: {status}, Duration: {self.duration}, Period: {self.period}")
            else:
                print(f" error status code : {response.status_code} ")

#TODO décider de la fréquence à laquelle le raspberry pi verifie si il doit activer la pompe
    

def main():
    actuator = Actuator(PUMP_PIN,1)
    actuator.initLoop()

if __name__ == "__main__":
    main()
        