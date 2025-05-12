from machine import I2C, Pin
from utime import sleep_ms


class AHT10:
    def __init__(self, i2c: I2C, i2c_address: int = 0x38) -> None:
        self._i2c = i2c
        self._i2c_address = i2c_address
        self._buffer = bytearray(6)
        self.reset()
        self.initialization()
        self.measurement()
        self.read()

    def reset(self) -> None:
        """Perform soft reset and"""
        sleep_ms(500)
        print(self._i2c.readfrom(self._i2c_address, 1))
        self._i2c.writeto(self._i2c_address, bytes([Command.SOFT_RESET]))
        sleep_ms(20)  # 20ms delay to wake up
        print(self._i2c.readfrom(self._i2c_address, 1))
        sleep_ms(500)
        print(self._i2c.readfrom(self._i2c_address, 1))

    def initialization(self) -> None:
        self._i2c.writeto(self._i2c_address, bytes([Command.INIT]))
        sleep_ms(200)

    def get_state(self) -> bytes:
        return self._i2c.readfrom(self._i2c_address, 1)

    def is_calibrated(self) -> bool:
        return self.get_state() & ...

    def measurement(self) -> None:
        self._i2c.writeto(self._i2c_address, bytes([Command.TRIGGER_MEASUREMENT]))
        sleep_ms(200)

    def read(self):
        self._i2c.readfrom_into(self._i2c_address, self._buffer)

        # print([byte for byte in self._buffer])


class Command:
    INIT = 0b11100001
    TRIGGER_MEASUREMENT = 0b10101100
    SOFT_RESET = 0b10111010


class StateMask:
    BUSY = 0b10000000
    MODE = 0b01100000
    CAL_ENABLE = 0b00001000


i2c = I2C(0, scl=Pin(9, pull=Pin.PULL_UP), sda=Pin(8, pull=Pin.PULL_UP))
sensor = AHT10(i2c=i2c)
# sensor

# i2c.writeto(0x38, bytes([Command.INIT]))
# sleep_ms(20)


# out = i2c.readfrom(0x38, 1)
# print(f"{int.from_bytes(out):08b}")

# i2c.writeto(0x38, bytes([Command.TRIGGER_MEASUREMENT]))


# out = i2c.readfrom(0x38, 1)
# print(f"{int.from_bytes(out):08b}")

# sleep_ms(150)

# i2c.readfrom_into(0x38, buffer)
# print(buffer)
# print(f"{int.from_bytes(buffer):08b}")
# print(f"{int.from_bytes(out):08b}")
