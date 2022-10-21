import pygame
from pygame.locals import *
from sys import exit
from colors import * 
import serial
import re
from datetime import datetime
import time
import json
from threading import Thread

# Serial setup
# port_name = input("Port name: ")
port_name = "COM3"
baud_rate = 2000000
try:
    ser = serial.Serial(port_name, baud_rate, timeout=1)
except: 
    print("Nao foi possivel abrir a porta serial")

# File JSON setup
# d = datetime.now()
# date_formatted = '{}-{}-{}-{}h{}'.format(d.year, d.month, d.day, d.hour, d.minute)
# sensorsJson = "results/sensors-" + date_formatted + ".json"    
# list_sensors = []
DATA = 0



def worker():
    global DATA
    while True:
        # processamento dos dados via serial
        data = ser.readline()
        if data: 
            print(data)
            DATA = data
        #     s_time = re.findall("#([0-9]+)", str(data))[0]
        #     S1 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[0]
        #     S2 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[1]
        #     S3 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[2]
        #     S4 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[3]
        #     S5 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[4]
        #     S6 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[5]
        #     encoder = re.findall("@(-*[0-9]*\.*[0-9]*)", str(data))[0]

        #     DATA = {
        #         "s_time": s_time,
        #         "S1": S1,
        #         "S2": S2,
        #         "S3": S3,
        #         "S4": S4,
        #         "S5": S5,
        #         "S6": S6,
        #         "encoder": encoder
        #     }
        #     list_sensors.append(DATA)

def end_game():
    # with open(sensorsJson, 'w') as file:
        # ser.write("0".encode())
        # ser.close()
        # json.dump(list_sensors, file)
        # time.sleep(0.5)
    pygame.quit()
    exit()

def create_fonts(font_sizes_list):
    "Creates different fonts with one list"
    fonts = []
    for size in font_sizes_list:
        fonts.append(
            pygame.font.SysFont("Arial", size))
    return fonts

def render(fnt, what, color, where):
    "Renders the fonts as passed from display_fps"
    text_to_show = fnt.render(what, 0, pygame.Color(color))
    screen.blit(text_to_show, where)

def display_fps():
    "Data that will be rendered and blitted in _display"
    render(
        fonts[0],
        what=str(int(clock.get_fps())),
        color="white",
        where=(5, 5))




t = Thread(target=worker)
t.daemon = True
t.start()

# init PyGame, init data acquisition
pygame.init()
ser.write("1".encode())

# Screen setup
WIDTH = 640
HEIGHT = 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()


fonts = create_fonts([32, 16, 14, 8])

game_running = True
while game_running:

    screen.fill(BLUE)
    display_fps()

    for event in pygame.event.get():
        if event.type == QUIT:
            end_game()

    

    
    clock.tick(60)
    pygame.display.flip()
