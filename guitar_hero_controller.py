# SPDX-FileCopyrightText: 2025 Modified by the-dvd
# SPDX-License-Identifier: MIT

"""
`guitar_hero_controller`
================================================================================

CircuitPython library for Guitar Hero Controller via I2C

* Based on Adafruit Nunchuk library by Carter Nelson
* Adapted for Guitar Hero Gibson Les Paul / World Tour controllers

**Hardware:**
- Guitar Hero Controller (Wii extension port)

**Software and Dependencies:**
- Adafruit CircuitPython firmware
- Adafruit BusDevice library
"""

import time
from collections import namedtuple
from adafruit_bus_device.i2c_device import I2CDevice

try:
    from busio import I2C
except ImportError:
    pass

__version__ = "1.0.0"
__repo__ = "https://github.com/the-dvd/circuitpython_guitar_hero_controller"

_I2C_INIT_DELAY = 0.1

class GuitarHeroController:
    """Interface for Guitar Hero Wii Controller via I2C"""

    _Values = namedtuple("Values", (
        "joystick", "whammy_bar", "touchbar", "strum", "frets", "buttons"
    ))

    _Joystick = namedtuple("Joystick", ("x", "y"))
    _Strum = namedtuple("Strum", ("up", "down"))
    _Frets = namedtuple("Frets", ("green", "red", "yellow", "blue", "orange"))
    _Buttons = namedtuple("Buttons", ("plus", "minus", "pedal"))

    def __init__(self, i2c: I2C, address: int = 0x52, i2c_read_delay: float = 0.002) -> None:
        self.buffer = bytearray(6)
        while not i2c.try_lock():
            pass
        _ = i2c.scan()
        i2c.unlock()

        self.i2c_device = I2CDevice(i2c, address)
        self._i2c_read_delay = i2c_read_delay
        time.sleep(_I2C_INIT_DELAY)
        with self.i2c_device as i2c_dev:
            i2c_dev.write(b"\xF0\x55")
            time.sleep(_I2C_INIT_DELAY)
            i2c_dev.write(b"\xFB\x00")

    @property
    def values(self) -> _Values:
        self._read_data()
        return self._Values(
            self.joystick,
            self.whammy_bar,
            self.touchbar,
            self.strum,
            self.frets,
            self.buttons
        )

    @property
    def joystick(self) -> _Joystick:
        return self._Joystick(self.buffer[0], self.buffer[1])

    @property
    def whammy_bar(self) -> int:
        return self.buffer[3] & 0x1F

    @property
    def touchbar(self) -> int:
        return self.buffer[2] & 0x1F

    @property
    def strum(self) -> _Strum:
        return self._Strum(
            not bool(self.buffer[5] & 0x01),  # BD - down
            not bool(self.buffer[4] & 0x40)   # BU - up
    )

    @property
    def frets(self) -> _Frets:
        return self._Frets(
            not bool(self.buffer[5] & 0x10),  # Green (bit 4)
            not bool(self.buffer[5] & 0x40),  # Red (bit 6)
            not bool(self.buffer[5] & 0x08),  # Yellow (bit 3)
            not bool(self.buffer[5] & 0x20),  # Blue (bit 5)
            not bool(self.buffer[5] & 0x80),  # Orange (bit 7)
    )

    @property
    def buttons(self) -> _Buttons:
        return self._Buttons(
            not bool(self.buffer[4] & 0x04),  # B+
            not bool(self.buffer[4] & 0x10),  # B-
            not bool(self.buffer[5] & 0x20),  # Pedal
        )

    def _read_data(self) -> bytearray:
        with self.i2c_device as i2c:
            i2c.write(b"\x00")
            time.sleep(self._i2c_read_delay)
            i2c.readinto(self.buffer)
        return self.buffer
