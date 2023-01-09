import serial
import re
from datetime import date, datetime, timedelta
import json
from consts import *

# ---------------------------------------------------------------------------------------------
# OVERVIEW
# ---------------------------------------------------------------------------------------------
# Script usado para testar a comunicação serial com o Arduino
# ---------------------------------------------------------------------------------------------
# FUNCIONAMENTO
# ---------------------------------------------------------------------------------------------
# Abre a porta serial, inicia a comunicação e recebe dados por 10 segundos
# Ao final, fecha a porta serial e cria um arquivo .json na mesma pasta de resultados
# Os dados recebidos são o tempo, os sensores de S1 a S6 e a posição do encoder
# ---------------------------------------------------------------------------------------------

d = datetime.now()
date_formatted = '{}_{}_{}_{}h{}m{}s'.format(d.year, d.month, d.day, d.hour, d.minute, d.second)
sensorsJson = "../results/sensors_" + date_formatted + ".json"  

list_sensors = []

t_start = datetime.now()

try:
    ser = serial.Serial(PORT_NAME, BAUD_RATE, timeout=2)
    print("Port open")
except: 
    print("Nao foi possivel abrir a porta serial")
    exit()

ser.write(b'1')

while (datetime.now() - t_start).seconds < 10:

    # dados vem na forma de #T,S1,S2,S3,S4,S5,S6@E
    data = ser.readline()
    
    # apenas processa os dados se recebeu alguma coisa
    if data: 
        print(data)
        
        s_time = re.findall("#([0-9]+)", str(data))[0]
        data_sensors = re.findall(",-*([0-9]*)", str(data))
        S1 = data_sensors[0]
        S2 = data_sensors[1]
        S3 = data_sensors[2]
        S4 = data_sensors[3]
        S5 = data_sensors[4]
        S6 = data_sensors[5]
        encoder = re.findall("@(-*[0-9]*)", str(data))[0]

        # dados formatados vem como um array de objetos no seguinte formato
        formatted_data = {
            "T": int(s_time),
            "S1": float(S1),
            "S2": float(S2),
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