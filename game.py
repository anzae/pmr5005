# PyGame imports
import pygame
from pygame.locals import *
from sys import exit
from colors import * 

# Data acquisition imports
import serial
import re
from datetime import datetime
import time
import json
from threading import Thread

### Serial setup
"""
    Setting up the serial communication with the handlebars. 
    Change the port name according to your computer or use terminal to input the port name
    The script will try to open the port, and end the program if failed
"""
# port_name = input("Port name: ")
port_name = "COM10"
baud_rate = 2000000
try:
    ser = serial.Serial(port_name, baud_rate, timeout=1)
except: 
    print("Nao foi possivel abrir a porta serial")
    exit()

### File JSON setup
"""
    The script creates a new file inside the results folder named "sensors-YYYY-MM-DD-HHhMM"
    This file will be soon used to save the data coming from the Arduino
"""
d = datetime.now()
date_formatted = '{}-{}-{}-{}h{}'.format(d.year, d.month, d.day, d.hour, d.minute)
sensorsJson = "results/sensors-" + date_formatted + ".json"    
list_sensors = []

global GAME_RUNNING
GAME_RUNNING = True
ENCODER = 0

# TODO: document this function
# this function is designed to be run in parallel with game main loop
def worker():
    while GAME_RUNNING:
        global ENCODER
        # data processing
        # data format: string #T,S1,S2,S3,S4,S5,S6@E\n * n
        data = ser.readline()
        if data: 
            T = re.findall("#([0-9]+)", str(data))[0]
            S1 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[0]
            S2 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[1]
            S3 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[2]
            S4 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[3]
            S5 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[4]
            S6 = re.findall(",([0-9]*\.*[0-9]*)", str(data))[5]
            E = re.findall("@(-*[0-9]*\.*[0-9]*)", str(data))[0]

            # new data format: JSON Array < {"T": T, S1": S1, "S2": S2, "S3": S3, "S4": S4, "S5": S5, "S6": S6, "E": E} >
            formatted_data = {
                "T": T,
                "S1": S1,
                "S2": S2,
                "S3": S3,
                "S4": S4,
                "S5": S5,
                "S6": S6,
                "E": E
            }
            list_sensors.append(formatted_data)

            ENCODER = int(E)

# TODO: document this function
def end_game():
    with open(sensorsJson, 'w') as file:
        ser.write("0".encode())
        ser.close()
        json.dump(list_sensors, file)
        time.sleep(0.5)
    pygame.quit()
    exit()

### THOSE 3 FUNCTIONS SHOULD BE MOVED TO CONTROLLER
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


### Thread start
"""
    This allows 'worker' to run in parallel with the game
    Otherwise the game won't run properly
"""
t = Thread(target=worker)
t.daemon = True
t.start()

### Initialization
"""
    Initializes PyGame and data acquisition
    Arduino is programmed to start sending data when it receives this value of "1".encode()
"""
pygame.init()
ser.write("1".encode()) 

### Screen setup
"""
    The screen is set up with width, height and caption
    Clock starts
    Fonts are created
"""
WIDTH = 640
HEIGHT = 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game PMR5005")
clock = pygame.time.Clock()
fonts = create_fonts([32, 16, 14, 8])


FPS = 60

x = 300


# TODO: find out why when running game.py for the second time without disconnecting Arduino, the game breaks when I try to close it
# TODO: NEXT STEP: create a box and make it move according to the encoder value

if __name__ == '__main__':
    # TODO: document this MAIN LOOP
    while GAME_RUNNING:

        screen.fill(BLUE)
        display_fps()

        for event in pygame.event.get():
            if event.type == QUIT:
                GAME_RUNNING = False
                end_game()
    
        clock.tick(FPS)
        dt = clock.tick(FPS) /1000


        # movimentação
        x = x - ENCODER * dt


        pygame.draw.rect(screen, RED, (x, 60, 40, 40))




        pygame.display.flip()
