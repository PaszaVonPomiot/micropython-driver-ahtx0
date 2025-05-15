# https://github.com/PaszaVonPomiot/micropython-driver-ahtx0
from machine import I2C
from utime import sleep_ms
from micropython import const


class Command:
    """Sensor commands."""

    INIT = (const(0xE1), const(0x08), const(0x00))
    TRIGGER_MEASUREMENT = (const(0xAC), const(0x33), const(0x00))
    SOFT_RESET = (const(0xBA),)


class StateMask:
    """Bit masks to extract chip state from state byte."""

    BUSY = const(0b10000000)
    MODE = const(0b01100000)
    CAL_ENABLE = const(0b00001000)


class AHT10:
    """Driver for AHT10 temperature and humidity sensor."""

    def __init__(self, i2c: I2C, i2c_address: int = 0x38) -> None:
        sleep_ms(20)  # power-on delay
        self._i2c = i2c
        self._i2c_address = i2c_address
        self._reset()
        self._buffer = bytearray(6)

    def _reset(self) -> None:
        """Perform soft reset and initialization."""
        self._i2c.writeto(self._i2c_address, bytes(Command.SOFT_RESET))
        sleep_ms(20)  # wake-up delay

    def _initialize(self) -> None:
        """Initialize and calibrate the sensor."""
        self._i2c.writeto(self._i2c_address, bytes(Command.INIT))

    def _measure(self) -> None:
        """Trigger a measurement and read results into buffer."""
        self._i2c.writeto(self._i2c_address, bytes(Command.TRIGGER_MEASUREMENT))
        sleep_ms(80)  # measurement time ~75 ms
        self._i2c.readfrom_into(self._i2c_address, self._buffer)

    def _get_raw_humidity_from_buffer(self) -> int:
        """Extract 20 bits of raw humidity from buffer."""
        return (self._buffer[1] << 12) | (self._buffer[2] << 4) | (self._buffer[3] >> 4)

    def _get_raw_temperature_from_buffer(self) -> int:
        """Extract 20 bits of raw temperature from buffer."""
        return (
            ((self._buffer[3] & 0x0F) << 16) | (self._buffer[4] << 8) | self._buffer[5]
        )

    def _calculate_humidity(self, raw_humidity: int) -> float:
        """Convert raw humidity to percentage."""
        return (raw_humidity / (1 << 20)) * 100

    def _calculate_temperature(self, raw_temperature: int) -> float:
        """Convert raw temperature to degrees Celsius."""
        return (raw_temperature / (1 << 20)) * 200 - 50

    def _get_state(self) -> int:
        """Read and return the state byte from the sensor."""
        return self._i2c.readfrom(self._i2c_address, 1)[0]

    def _is_busy(self) -> bool:
        """Check if the sensor is busy. Measurement results cannot be read while sensor is busy."""
        state = self._get_state()
        return bool(state & StateMask.BUSY)

    def _is_calibrated(self) -> bool:
        """Check if the sensor is calibrated. Chip is calibrated during initialization."""
        state = self._get_state()
        return bool(state & StateMask.CAL_ENABLE)

    @property
    def temperature(self) -> float:
        """
        Return temperature reading. Use this only if you won't use humidity,
        otherwise get both readings from `reading` property.
        """
        self._measure()
        raw_temperature = self._get_raw_temperature_from_buffer()
        return self._calculate_temperature(raw_temperature=raw_temperature)

    @property
    def humidity(self) -> float:
        """
        Return humidity reading. Use this only if you won't use temperature,
        otherwise get both readings from `reading` property.
        """
        self._measure()
        raw_humidity = self._get_raw_humidity_from_buffer()
        return self._calculate_humidity(raw_humidity=raw_humidity)

    @property
    def readings(self) -> tuple[float, float]:
        """Return temperature (Celsius) and relative humidity (%) readings."""
        self._measure()
        return self._calculate_temperature(
            raw_temperature=self._get_raw_temperature_from_buffer()
        ), self._calculate_humidity(raw_humidity=self._get_raw_humidity_from_buffer())
