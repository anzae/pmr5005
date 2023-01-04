# IMPORTANT CONFIGURATIONS
# -----------------------------------------------------------------------------------------------
# Configurações importantes para serem verificadas a cada sessão.
# -----------------------------------------------------------------------------------------------
TOGGLE_SERIAL = False        # Uso ou não da porta serial, só funciona se estiver com o Arduino
PORT_NAME = "COM3"          # Nome da porta serial que vai ser usada, caso esteja com Arduino
LEVEL = 3                   # Level do jogo, de 0 a 3
# -----------------------------------------------------------------------------------------------

# Arduino configuration
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

# Sprite size constants
COIN_SIZE_W = 20
COIN_SIZE_H = 24
SPIKE_SIZE = 120
WIND_SIZE = 40

# Level configs
COINS_CONFIG = 'levels/level_{}/coins.json'.format(str(LEVEL))
SPIKES_CONFIG = 'levels/level_{}/spikes.json'.format(str(LEVEL))
WIND_CONFIG = 'levels/level_{}/wind.json'.format(str(LEVEL))