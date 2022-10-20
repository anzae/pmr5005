import serial
import re
from datetime import datetime
import json


# port_name = input("Port name: ")
port_name = "COM3"
baud_rate = 115200

d = datetime.now()
date_formatted = '{}-{}-{}-{}h{}'.format(d.year, d.month, d.day, d.hour, d.minute)
sensorsJson = "results/sensors-" + date_formatted + ".json"  

list_sensors = []


try:
    ser = serial.Serial(port_name, baud_rate, timeout=1)
except: 
    print("Nao foi possivel abrir a porta serial")

while True:
    serial_bytes = ser.in_waiting
    # dados vem na forma de #T,S1,S2,S3,S4,S5,S6@E
    data = ser.read(serial_bytes)
    
    # only processes data when receives something
    if data: 
        
        s_time = re.findall("#([0-9]+)", str(data))[0]
        S1 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[0]
        S2 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[1]
        S3 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[2]
        S4 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[3]
        S5 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[4]
        S6 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[5]
        encoder = re.findall("@([0-9]*\.*[0-9]*)", str(data))[0]


        formatted_data = {
            "s_time": s_time,
            "S1": S1,
            "S2": S2,
            "S3": S3,
            "S4": S4,
            "S5": S5,
            "S6": S6,
            "encoder": encoder
        }

        list_sensors.append(formatted_data)
        

    with open(sensorsJson, 'w') as file:       
        json.dump(list_sensors, file)