# PyGame imports
import pygame
from pygame.locals import *
from sys import exit
from consts import * 
from controller import *

# Data acquisition imports
import serial
import re
from datetime import datetime
import time
import json
from threading import Thread

if TOGGLE_SERIAL: 
    ### Serial setup
    """
        Setting up the serial communication with the handlebars. 
        Change the port name according to your computer or use terminal to input the port name
        The script will try to open the port, and end the program if failed
    """
    try:
        ser = serial.Serial(PORT_NAME, BAUD_RATE, timeout=1)
    except: 
        print("Nao foi possivel abrir a porta serial")
        exit()

    ### JSON file setup
    """
        The script creates a new file inside the results folder named "sensors-YYYY-MM-DD-HHhMM"
        This file will be soon used to save the data coming from the Arduino
    """
    d = datetime.now()
    date_formatted = '{}-{}-{}-{}h{}'.format(d.year, d.month, d.day, d.hour, d.minute)
    sensorsJson = "results/sensors-" + date_formatted + ".json"    
    list_sensors = []

    ENCODER = 0

# global GAME_RUNNING
GAME_RUNNING = True

# TODO: document this function
# this function is designed to be run in parallel with game main loop
def worker():
    while GAME_RUNNING:
        global ENCODER

        # data processing
        # data format: string #T,S1,S2,S3,S4,S5,S6@E\n 
        data = ser.readline()
        if data: 
            T = re.findall("#([0-9]+)", str(data))[0]
            S1 = re.findall(",([0-9]*)", str(data))[0]
            S2 = re.findall(",([0-9]*)", str(data))[1]
            S3 = re.findall(",([0-9]*)", str(data))[2]
            S4 = re.findall(",([0-9]*)", str(data))[3]
            S5 = re.findall(",([0-9]*)", str(data))[4]
            S6 = re.findall(",([0-9]*)", str(data))[5]
            E = re.findall("@(-*[0-9]*)", str(data))[0]

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
    if TOGGLE_SERIAL:
        with open(sensorsJson, 'w') as file:
            end_serial()
            json.dump(list_sensors, file)
    time.sleep(0.5)
    pygame.quit()
    exit()

### Functions to display FPS in game
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
        where=(10, 5))

if TOGGLE_SERIAL:
    ### Thread start
    """
        This allows 'worker' to run in parallel with the game
        Otherwise the game won't run properly
    """
    t = Thread(target=worker)
    t.daemon = True
    t.start()

### Initialization and Screen setup
"""
    The screen is set up with width, height and caption
    Clock starts
    Fonts are created
"""
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game PMR5005")
clock = pygame.time.Clock()
fonts = create_fonts([32, 16, 14, 8])

### Menu Screen
"""
    Renders menu screen with start button
"""
def menu():
    background = pygame.transform.scale(pygame.image.load('assets/cloud_bg.png'), (WIDTH, HEIGHT))
    play_button = pygame.transform.scale(pygame.image.load('assets/start_button.png'), (60, 30))
    while True:
        screen.blit(background, (0,0))
        screen.blit(play_button, (300, 200))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] in range(300, 360) and event.pos[1] in range(200, 230):
                    play()


def play():

    global GAME_RUNNING

    if TOGGLE_SERIAL:
        start_serial(ser)

    x_position = 300
    y_position = 80
    y_bg = 0

    while GAME_RUNNING:

        bg = pygame.transform.scale(pygame.image.load('assets/cloud_bg2.png'), (WIDTH, HEIGHT))
        ground = pygame.transform.scale(pygame.image.load('assets/ground.png'), (WIDTH, HEIGHT))

        for i in range(BACKGROUND_NUMBER):
            screen.blit(bg, (0, y_bg + HEIGHT * i))
        screen.blit(ground, (0, y_bg + HEIGHT * BACKGROUND_NUMBER))


        y_bg -= FALL_SPEED
        
        if y_bg < -HEIGHT * BACKGROUND_NUMBER:
            y_bg = -HEIGHT * BACKGROUND_NUMBER
            y_position += FALL_SPEED

        if y_position > HEIGHT / 2 + 5: # + 5: small adjustment to ground imagea
            y_position = HEIGHT / 2 + 5
            time.sleep(0.5) # talvez adicionar uma função indicando fim do jogo graficamente na tela
            end_game()

            


        display_fps()

        for event in pygame.event.get():
            if event.type == QUIT:
                GAME_RUNNING = False
                end_game()

        clock.tick(FPS)
        dt = clock.tick(FPS) /1000

        # movimentação
        if TOGGLE_SERIAL:
            x_position = x_position - ENCODER * dt
        else:
            if pygame.key.get_pressed()[K_a]:
                x_position = x_position - 500 * dt
                
            if pygame.key.get_pressed()[K_d]:
                x_position = x_position + 500 * dt
                
        # keep player inside screen 
        if x_position > WIDTH - PLAYER_W:
            x_position = WIDTH - PLAYER_W
        if x_position < 0:
            x_position = 0


        pygame.draw.rect(screen, RED, (x_position, y_position, PLAYER_W, PLAYER_H))

        pygame.display.flip()


menu()