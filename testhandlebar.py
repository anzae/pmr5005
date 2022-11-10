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
        data_sensors = re.findall(",([0-9]*)", str(data))
        S1 = data_sensors[0]
        S2 = data_sensors[1]
        S3 = data_sensors[2]
        S4 = data_sensors[3]
        S5 = data_sensors[4]
        S6 = data_sensors[5]
        encoder = re.findall("@(-*[0-9]*)", str(data))[0]

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