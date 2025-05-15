import utime
from machine import Pin, I2C

from lib.ahtx0 import AHT10


def main() -> None:
    i2c = I2C(0, scl=Pin(9, pull=Pin.PULL_UP), sda=Pin(8, pull=Pin.PULL_UP))
    sensor = AHT10(i2c=i2c)

    while True:
        print(f"{sensor.temperature:.2f}, {sensor.humidity:.2f}")


if __name__ == "__main__":
    main()
