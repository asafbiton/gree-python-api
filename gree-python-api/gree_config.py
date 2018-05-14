from exceptions import InvalidConfigValue


class GreeConfig:
    MIN_TEMP = 0  # TODO: find real
    MAX_TEMP = 30  # TODO: find real

    MIN_FAN_SPEED = 0
    MAX_FAN_SPEED = 5

    MIN_SWING = 0
    MAX_SWING = 11

    MODES = {
        "auto": 0,
        "cool": 1,
        "dry": 2,
        "fan": 3,
        "heat": 4
    }

    def __init__(self, config=None):
        self._config = config or {}
        self._config_mapping = {
            'power': self.set_power_on,
            'temperature': self.set_temperature,
            'mode': self.set_mode,
            'quiet': self.set_quiet_mode_enabled,
            'turbo': self.set_turbo_mode_enabled,
            'fanSpeed': self.set_fan_speed,
            'lights': self.set_display_enabled,
            'swing': self.set_swing,
            'health': self.set_health_mode_enabled,
            'blow': self.set_blow_mode_enabled,
            'air_valve': self.set_air_valve_enabled,
            'energy_saving': self.set_energy_saving_enabled
        }

    @property
    def config(self):
        return self._config

    @property
    def temperature(self):
        if "SetTem" in self._config.keys():
            return self._config["SetTem"]
        return False

    @temperature.setter
    def temperature(self, temperature):
        self.__set_temperature(temperature)

    @property
    def mode(self):
        if "Mod" in self._config.keys():
            return self._config["Mod"]  # TODO: return key instead of int value?
        return False

    @mode.setter
    def mode(self, mode):
        self.__set_mode(mode)

    @property
    def is_quiet(self):
        if "Quiet" in self._config.keys():
            return self._config["Quiet"] == 1
        return False

    @is_quiet.setter
    def is_quiet(self, is_quiet):
        self.__set_quiet_mode_enabled(is_quiet)

    # TODO: create general set_bool

    def set_power_on(self, enabled=True):
        if type(enabled) != bool:
            raise InvalidConfigValue(f"Invalid config value received: {enabled}")

        self._config["Pow"] = int(enabled)

    def __set_mode(self, mode):
        if type(mode) == int and mode not in self.MODES.values():
            raise InvalidConfigValue(f"Mode {mode} is not a valid mode")

        self._config["Mod"] = self.MODES[mode]

    def __set_temperature(self, temp, unit="c"):
        if unit != "c" or unit != "f":
            raise InvalidConfigValue(f"Unit {unit} is an invalid unit.")

        if type(temp) != int or temp < self.MIN_TEMP or temp > self.MAX_TEMP:
            raise InvalidConfigValue(f"Temperature {temp} is invalid or "
                                     f"not in range ({self.MIN_TEMP} - {self.MAX_TEMP}).")

        self._config["TemUn"] = 1 if unit == "f" else 0
        self._config["SetTem"] = temp

    def set_fan_speed(self, speed):
        if type(speed) != int or speed < self.MIN_FAN_SPEED or speed > self.MAX_FAN_SPEED:
            raise InvalidConfigValue(f"Speed {speed} is either invalid or "
                                     f"not in range ({self.MIN_FAN_SPEED} - {self.MAX_FAN_SPEED}).")

        self._config["WdSpd"] = speed

    def set_display_enabled(self, enabled):
        if type(enabled) != bool:
            raise InvalidConfigValue(f"Invalid config value received: {enabled}")

        self._config["Lig"] = int(enabled)

    def __set_quiet_mode_enabled(self, enabled):
        if type(enabled) != bool:
            raise InvalidConfigValue(f"Invalid config value received: {enabled}")

        self._config["Quiet"] = int(enabled)

    def set_turbo_mode_enabled(self, enabled):
        if type(enabled) != bool:
            raise InvalidConfigValue(f"Invalid config value received: {enabled}")

        self._config["Tur"] = int(enabled)

    def set_energy_saving_enabled(self, enabled):
        if type(enabled) != bool:
            raise InvalidConfigValue(f"Invalid config value received: {enabled}")

        self._config["SvSt"] = int(enabled)

    def set_swing(self, swing):
        """
        Sets AC swing, according to the following map:
        0: default
        1: swing in full range
        2: fixed in the upmost position (1/5)
        3: fixed in the middle-up position (2/5)
        4: fixed in the middle position (3/5)
        5: fixed in the middle-low position (4/5)
        6: fixed in the lowest position (5/5)
        7: swing in the downmost region (5/5)
        8: swing in the middle-low region (4/5)
        9: swing in the middle region (3/5)
        10: swing in the middle-up region (2/5)
        11: swing in the upmost region (1/5)
        :param swing: the index of the desired swing operation
        :return:
        """
        if type(swing) != int or swing < self.MIN_SWING or swing > self.MAX_SWING:
            raise InvalidConfigValue(f"Swing {swing} is either invalid or "
                                     f"not in range ({self.MIN_SWING} - {self.MAX_SWING}).")

        self._config["SwUpDn"] = int(swing)

    def set_health_mode_enabled(self, enabled):
        if type(enabled) != bool:
            raise InvalidConfigValue(f"Invalid config value received: {enabled}")

        self._config["Health"] = int(enabled)

    def set_blow_mode_enabled(self, enabled):
        if type(enabled) != bool:
            raise InvalidConfigValue(f"Invalid config value received: {enabled}")

        self._config["Blo"] = int(enabled)

    def set_air_valve_enabled(self, enabled):
        if type(enabled) != bool:
            raise InvalidConfigValue(f"Invalid config value received: {enabled}")

        self._config["Air"] = int(enabled)