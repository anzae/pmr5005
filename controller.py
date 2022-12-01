from datetime import datetime
from consts import *
import pygame
from pygame.locals import *

# O programa do Arduino começa a enviar dados quando recebe 1 pela porta serial
def start_serial(serial):
    serial.write("1".encode())

# O programa do Arduino para de enviar dados quando recebe 0 pela porta serial
def end_serial(serial):
    serial.write(b'0')
    serial.close()

def create_fonts(font_sizes_list):
    "Creates different fonts with one list"
    fonts = []
    for size in font_sizes_list:
        fonts.append(
            pygame.font.SysFont("Arial", size))
    return fonts

def collect_coin(score, player, coin):
    if pygame.sprite.collide_rect(player, coin):
        score += 1
        coin.collected = True
    return score

def hit_spike(lives, player, spike):
    if pygame.sprite.collide_rect(player, spike) and spike.active:
        lives -= 1
        spike.active = False
    return lives

def enter_wind(player, wind):
    if pygame.sprite.collide_rect(player, wind):
        return True
    return False

class Entity(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

class Player(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load('assets/player_dog.png'), (PLAYER_W, PLAYER_H))
        self.x = x
        self.y = y
        self.rect = Rect(x + PLAYER_W/3 + 2, y+PLAYER_H*2/5, PLAYER_W/3, PLAYER_H*3/5)

class Coin(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load('assets/coin.png'), (COIN_SIZE_W, COIN_SIZE_H))
        self.x = x
        self.y = y
        self.collected = False
        self.rect = Rect(x, y, COIN_SIZE_W, COIN_SIZE_H)      

    def update(self):
        if self.collected:
            self.kill()

class Spike(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load('assets/spike.png'), (SPIKE_SIZE, SPIKE_SIZE))
        self.x = x
        self.y = y
        self.active = True
        self.rect = Rect(x, y, SPIKE_SIZE, SPIKE_SIZE)

class Wind(Entity):
    def __init__(self, y_start, y_end, magnitude):
        Entity.__init__(self)
        # to cover area we need to blit in a loop
        self.image_l = pygame.transform.scale(pygame.image.load('assets/wind_l.png'), (WIND_SIZE, WIND_SIZE)).convert_alpha()
        self.image_r = pygame.transform.scale(pygame.image.load('assets/wind_r.png'), (WIND_SIZE, WIND_SIZE)).convert_alpha()
        self.image_l.set_alpha(30)
        self.image_r.set_alpha(30)
        self.y_start = y_start
        self.y_end = y_end
        self.magnitude = magnitude
        self.rect = Rect(0, y_start, WIDTH, y_end-y_start)
