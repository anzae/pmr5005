# Control whether the serial port is being used or not. Mostly for test usage
TOGGLE_SERIAL = False

# Serial constants
PORT_NAME = "COM10"
BAUD_RATE = 2000000

# Game constants
WIDTH = 640
HEIGHT = 480
FPS = 60
BACKGROUND_NUMBER = 5
TOTAL_HEIGHT = HEIGHT * (BACKGROUND_NUMBER + 1)
BUTTON_W = 60
BUTTON_H = 30

# Player constants
PLAYER_W = 80
PLAYER_H = 100
FALL_SPEED = 5
SCORE = 0
LIVES = 2
VELOCITY_MULTIPLIER = 5

# Sprite constants
COIN_SIZE_W = 20
COIN_SIZE_H = 24
SPIKE_SIZE = 120
WIND_SIZE = 40

# Level configs
LEVEL = 'level_2'
COINS_CONFIG = '{}/coins.json'.format(LEVEL)
SPIKES_CONFIG = '{}/spikes.json'.format(LEVEL)
WIND_CONFIG = '{}/wind.json'.format(LEVEL)