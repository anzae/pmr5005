import serial
import re
import time
from datetime import datetime
import json

# O programa do Arduino começa a enviar dados quando recebe 1 pela porta serial
def start_serial(serial):
    serial.write(1)

# O programa do Arduino para de enviar dados quando recebe 0 pela porta serial
def end_serial(serial):
    serial.write(0)
    serial.close()

# testar com o encoder real onde é o zero e onde é o 180 e fazer a conversão direito
def get_angular_position(encoder):
    return encoder / 2000 - 90

def set_velocity(player, encoder):
    # nao sei se é assim
    angular_position = get_angular_position(encoder)
    player.velx += angular_position
    # depois tem que setar a posição fazendo pos += velocidade * deltaT