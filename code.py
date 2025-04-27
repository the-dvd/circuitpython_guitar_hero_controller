import board
import busio
import time
from guitar_hero_controller import GuitarHeroController

i2c = busio.I2C(board.GP1, board.GP0)
guitar = GuitarHeroController(i2c)

while True:
    vals = guitar.values
    print("Joystick:", vals.joystick)
    print("Frets:", vals.frets)
    print("Whammy:", vals.whammy_bar)
    print("Touchbar:", vals.touchbar)
    print("Strum:", vals.strum)
    print("Buttons:", vals.buttons)
    time.sleep(0.2)
