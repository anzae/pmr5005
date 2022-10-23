from datetime import datetime
from consts import *
import pygame
from pygame.locals import *
import time

# O programa do Arduino começa a enviar dados quando recebe 1 pela porta serial
def start_serial(serial):
    serial.write("1".encode())

# O programa do Arduino para de enviar dados quando recebe 0 pela porta serial
def end_serial(serial):
    serial.write("0".encode())
    serial.close()

# testar com o encoder real onde é o zero e onde é o 180 e fazer a conversão direito
def get_angular_position(encoder):
    return encoder * 3 / 20

def set_velocity(player, encoder):
    # nao sei se é assim
    const = 0.2
    angular_position = get_angular_position(encoder)
    player.velx += angular_position * const
    # depois tem que setar a posição fazendo pos += velocidade * deltaT

def create_fonts(font_sizes_list):
    "Creates different fonts with one list"
    fonts = []
    for size in font_sizes_list:
        fonts.append(
            pygame.font.SysFont("Arial", size))
    return fonts
