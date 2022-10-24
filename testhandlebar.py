import serial
import re
from datetime import date, datetime, timedelta
import json
from consts import *

port_name = PORT_NAME
baud_rate = BAUD_RATE

d = datetime.now()
date_formatted = '{}-{}-{}-{}h{}'.format(d.year, d.month, d.day, d.hour, d.minute)
sensorsJson = "results/sensors-" + date_formatted + ".json"  

list_sensors = []

t_start = datetime.now()

try:
    ser = serial.Serial(port_name, baud_rate, timeout=2)
    print("Port open")
except: 
    print("Nao foi possivel abrir a porta serial")
    exit()

ser.write("1".encode())

while (datetime.now() - t_start).seconds < 10:

    # dados vem na forma de #T,S1,S2,S3,S4,S5,S6@E
    data = ser.readline()
    
    # only processes data when receives something
    if data: 
        print(data)
        
        s_time = re.findall("#([0-9]+)", str(data))[0]
        S1 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[0]
        S2 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[1]
        S3 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[2]
        S4 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[3]
        S5 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[4]
        S6 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[5]
        encoder = re.findall("@(-*[0-9]*\.*[0-9]*)", str(data))[0]

        formatted_data = {
            "T": int(s_time),
            "S1": int(S1),
            "S2": int(S2),
            "S3": int(S3),
            "S4": int(S4),
            "S5": int(S5),
            "S6": int(S6),
            "E": int(encoder)
        }

        list_sensors.append(formatted_data)
        
    with open(sensorsJson, 'w') as file:       
        json.dump(list_sensors, file)

ser.write("0".encode())
ser.close()