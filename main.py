import utime
from machine import Pin, I2C

from lib.ahtx0 import ahtx0


def main():
    i2c = I2C(scl=Pin(9), sda=Pin(8))
    sensor = ahtx0.AHT10(i2c)

    while True:
        print(f"{sensor.temperature:.2f}, {sensor.relative_humidity:.2f}")
        utime.sleep(0.1)


if __name__ == "__main__":
    main()
