# PyGame imports
import pygame
from pygame.locals import *
from sys import exit
import time
from consts import * 
from controller import *

# Data acquisition imports
import serial
import re
from datetime import datetime
import json

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
    IMPEDANCE = ''

# global GAME_RUNNING
GAME_RUNNING = True

# TODO fix this function
# wind must have an impedance property and when player collides with wind, variable impedance must be set
# when there's no collision, impedance must return to zero ('c')
def impedance():
    while GAME_RUNNING:
        global IMPEDANCE

        # 5 niveis de "impedancia": a, b, c, d, e
        # a -> -30, b: -15, c-> 0, d-> 15, e: 30
        # arrumar para o guidão forçar nessas posições

        if IMPEDANCE == 'a':
            serial.write('a'.encode())
        if IMPEDANCE == 'b':
            serial.write('b'.encode())
        if IMPEDANCE == 'c':
            serial.write('c'.encode())
        if IMPEDANCE == 'd':
            serial.write('d'.encode())
        if IMPEDANCE == 'e':
            serial.write('e'.encode())

def end_game():
    """
        Function to run when the game ends. 
        It opens the json file and saves data from the sensors, then closes the game and ends the program.
    """
    if TOGGLE_SERIAL:
        with open(sensorsJson, 'w') as file:
            end_serial(ser)
            json.dump(list_sensors, file)
    time.sleep(0.5)
    pygame.quit()
    exit()

### Functions to display hud in game
def render(fnt, what, color, where):
    # "Renders the fonts as passed from display_fps"
    text_to_show = fnt.render(what, 0, pygame.Color(color))
    # TODO: rectangle with transparency to better visualize the hud
    screen.blit(text_to_show, where)

def display_hud(score, lives, height):
    render(
        fonts[1],
        what="LIVES: {}".format(lives),
        color="black",
        where=(15, 5))
    render(
        fonts[1],
        what="FPS: {}".format(int(clock.get_fps())),
        color="black",
        where=(200, 5))
    render(
        fonts[1],
        what="Height: {}".format(height),
        color="black",
        where=(350, 5))
    render(
        fonts[1],
        what="SCORE: {}".format(score),
        color="black",
        where=(560, 5))

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
    play_button = pygame.transform.scale(pygame.image.load('assets/start_button.png'), (BUTTON_W, BUTTON_H))
    while True:
        screen.blit(background, (0,0))
        screen.blit(play_button, (WIDTH/2 - BUTTON_W/2, HEIGHT/2 - BUTTON_H/2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] in range(int(WIDTH/2-BUTTON_W/2), int(WIDTH/2+BUTTON_W/2)) and event.pos[1] in range(int(HEIGHT/2-BUTTON_H/2), int(HEIGHT/2+BUTTON_H/2)):
                    play()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                play()

def play():

    global GAME_RUNNING
    start = False

    if TOGGLE_SERIAL:
        start_serial(ser)
    
    coins = []
    spikes = []
    winds = []
    coins_group = pygame.sprite.Group()
    spikes_group = pygame.sprite.Group()
    winds_group = pygame.sprite.Group()
    wind_repeats_x = int(WIDTH/WIND_SIZE)    

    score = SCORE
    lives = LIVES

    # Level builder
    with open(COINS_CONFIG, 'r') as coins_config:
        file = json.load(coins_config)
        for i in file:
            coin = Coin(i["x"], i["y"])
            coins.append(coin)
            coins_group.add(coin)
    with open(SPIKES_CONFIG, 'r') as spikes_config:
        file = json.load(spikes_config)
        for i in file:
            spike = Spike(i["x"], i["y"])
            spikes.append(spike)
            spikes_group.add(spike)
    with open(WIND_CONFIG, 'r') as wind_config:
        file = json.load(wind_config)
        for i in file:
            wind = Wind(i["y_start"], i["y_end"], i["magnitude"])
            winds.append(wind)
            winds_group.add(wind)

    # Player's initial positions
    x_position = 280
    y_position = 80
    player = Player(x_position, y_position)

    # Scroller's initial positions: background and winds
    y_bg = 0
    x_bg_wind = [0] * len(winds)

    # Background
    bg = pygame.transform.scale(pygame.image.load('assets/cloud_bg.png'), (WIDTH, HEIGHT))
    ground = pygame.transform.scale(pygame.image.load('assets/ground.png'), (WIDTH, HEIGHT))

### MAIN LOOP ###
    while GAME_RUNNING:

    ### SERIAL COMMUNICATION ###
        if TOGGLE_SERIAL:
            data = ser.readline()
            if data: 
                data_sensors = re.findall(",-*([0-9]*)", str(data))
                T = re.findall("#([0-9]+)", str(data))[0]
                S1 = data_sensors[0]
                S2 = data_sensors[1]
                S3 = data_sensors[2]
                S4 = data_sensors[3]
                S5 = data_sensors[4]
                S6 = data_sensors[5]
                E = re.findall("@(-*[0-9]*)", str(data))[0]

                # new data format: JSON Array < {"T": T, S1": S1, "S2": S2, "S3": S3, "S4": S4, "S5": S5, "S6": S6, "E": E} >
                formatted_data = {
                    "T": int(T),
                    "S1": int(S1),
                    "S2": int(S2),
                    "S3": int(S3),
                    "S4": int(S4),
                    "S5": int(S5),
                    "S6": int(S6),
                    "E": int(E)
                }
                list_sensors.append(formatted_data)
                ENCODER = int(E)

    ### QUIT EVENT ###
        for event in pygame.event.get():
            if event.type == QUIT:
                GAME_RUNNING = False
                end_game()

    ### BACKGROUND ###
        # Build background
        for i in range(BACKGROUND_NUMBER):
            screen.blit(bg, (0, y_bg + HEIGHT * i))
        screen.blit(ground, (0, y_bg + HEIGHT * BACKGROUND_NUMBER))

        # Background auto scroller
        y_bg -= FALL_SPEED
        if y_bg < -HEIGHT * BACKGROUND_NUMBER:
            y_bg = -HEIGHT * BACKGROUND_NUMBER
            y_position += FALL_SPEED
            player.rect.y += FALL_SPEED
        if y_position > HEIGHT / 2 - 20: # adjustment to ground image
            y_position = HEIGHT / 2 - 20
            print("Score: ", score)
            time.sleep(0.5) # talvez adicionar uma função indicando fim do jogo graficamente na tela
            end_game()

    ### CLOCK and FPS ###
        clock.tick(FPS)
        dt = clock.tick(FPS) /1000

    ### SPRITES ###
        for coin in coins_group:
            screen.blit(coin.image, (coin.x, coin.y + y_bg))
        for spike in spikes_group:
            screen.blit(spike.image, (spike.x, spike.y + y_bg))
        idx = 0
        for wind in winds_group:
            img = wind.image_r if wind.magnitude > 0 else wind.image_l
            wind_repeats_y = int((wind.y_end - wind.y_start)/WIND_SIZE)
            # infinite wind x-scroll
            x_bg_wind[idx] += wind.magnitude
            for x in range(wind_repeats_x):
                x_repeats = x*WIND_SIZE + x_bg_wind[idx]
                for y in range(wind_repeats_y):
                    y_repeats = wind.y_start + y*WIND_SIZE + y_bg
                    screen.blit(img, (x_repeats, y_repeats))
                    screen.blit(img, (x_repeats + WIDTH, y_repeats))
                    screen.blit(img, (x_repeats - WIDTH, y_repeats))
                if x_bg_wind[idx] <= -WIDTH:
                    x_bg_wind[idx] = 0
                if x_bg_wind[idx] >= WIDTH:
                    x_bg_wind[idx] = 0
            idx += 1

    ### PLAYER ###
        # Keep player inside screen 
        if x_position > WIDTH - PLAYER_W:
            x_position = WIDTH - PLAYER_W
        if x_position < 0:
            x_position = 0

        # Change rect attributes
        player.rect.x = x_position + PLAYER_W/3 + 2
        for coin in coins_group:
            coin.rect.y -= FALL_SPEED
        for spike in spikes_group:
            spike.rect.y -= FALL_SPEED
        for wind in winds_group:
            wind.rect.y -= FALL_SPEED

        # Game over
        if lives == 0:
            print("Score: ", score)
            end_game()

    ### UPDATE ###
        # Entities update
        wind_collider = False
        player.update(spikes)
        for coin in coins_group:
            score = collect_coin(score, player, coin)
            coin.update()
        for spike in spikes_group:
            lives = hit_spike(lives, player, spike)
        for wind in winds_group:
            if enter_wind(wind, player):
                wind_collider = True
                wind_mag = wind.magnitude
        if wind_collider: 
            wind_vel = wind_mag
        else:
            wind_vel = 0

        wind_collider = False

        # Player movement
        if TOGGLE_SERIAL:
            x_position -= ENCODER * VELOCITY_MULTIPLIER * dt 
        else:
            if pygame.key.get_pressed()[K_a]:
                x_position = x_position - 800 * dt
            if pygame.key.get_pressed()[K_d]:
                x_position = x_position + 800 * dt 
        x_position += wind_vel
        
        # Game update
        game_h = TOTAL_HEIGHT + y_bg - y_position - PLAYER_H - 160 # adjustment to be 0 when player hits the ground
        display_hud(score, lives, game_h)
        screen.blit(player.image, (x_position, y_position))
        pygame.display.update()
        if not start:
            time.sleep(0.5)
            start = True

if __name__ == '__main__':
    menu()