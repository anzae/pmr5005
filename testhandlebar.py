import serial
import re
from datetime import date, datetime, timedelta
import json
import time


# port_name = input("Port name: ")
port_name = "COM3"
baud_rate = 2000000

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

while (datetime.now() - t_start).seconds < 5:
    serial_bytes = ser.in_waiting
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

ser.write("0".encode())
ser.close()