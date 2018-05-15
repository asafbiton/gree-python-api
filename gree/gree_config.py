from .exceptions import InvalidConfigValue


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

    # Properties
    @property
    def config(self):
        return self._config

    @property
    def power_on(self):
        if "Pow" in self._config.keys():
            return self._config["Pow"]

    @power_on.setter
    def power_on(self, enabled):
        self.__set_bool("Pow", enabled)

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
    def quiet_mode_enabled(self):
        if "Quiet" in self._config.keys():
            return self._config["Quiet"] == 1
        return False

    @quiet_mode_enabled.setter
    def quiet_mode_enabled(self, enabled):
        self.__set_bool("Quiet", enabled)

    @property
    def fan_speed(self):
        if "WdSpd" in self._config.keys():
            return self._config["WdSpd"]
        return False

    @fan_speed.setter
    def fan_speed(self, fan_speed):
        self.__set_fan_speed(fan_speed)

    @property
    def display_enabled(self):
        if "Lig" in self._config.keys():
            return self._config["Lig"]
        return False

    @display_enabled.setter
    def display_enabled(self, enabled):
        self.__set_bool("Lig", enabled)

    @property
    def turbo_mode_enabled(self):
        if "Tur" in self._config.keys():
            return self._config["Tur"]
        return False

    @turbo_mode_enabled.setter
    def turbo_mode_enabled(self, enabled):
        self.__set_bool("Tur", enabled)

    @property
    def energy_saving_enabled(self):
        if "SvSt" in self._config.keys():
            return self._config["SvSt"]
        return False

    @energy_saving_enabled.setter
    def energy_saving_enabled(self, enabled):
        self.__set_bool("SvSt", enabled)

    @property
    def swing(self):
        if "SwUpDn" in self._config.keys():
            return self._config["SwUpDn"]
        return False

    @swing.setter
    def swing(self, swing):
        self.__set_swing(swing)

    @property
    def health_mode_enabled(self):
        if "Health" in self._config.keys():
            return self._config["Health"]
        return False

    @health_mode_enabled.setter
    def health_mode_enabled(self, enabled):
        self.__set_bool("Health", enabled)

    @property
    def blow_mode_enabled(self):
        if "Blo" in self._config.keys():
            return self._config["Blo"]
        return False

    @blow_mode_enabled.setter
    def blow_mode_enabled(self, enabled):
        self.__set_bool("Blo", enabled)

    @property
    def air_valve_enabled(self):
        if "Air" in self._config.keys():
            return self._config["Air"]
        return False

    @air_valve_enabled.setter
    def air_valve_enabled(self, enabled):
        self.__set_bool("Air", enabled)

    # Private methods
    def __set_mode(self, mode):
        if (mode is int and mode not in self.MODES.values()) or \
                (mode is str and mode not in self.MODES.keys()):
            raise InvalidConfigValue(f"Mode {mode} is not a valid mode")

        if mode is str:
            mode = self.MODES[mode]

        self._config["Mod"] = mode

    def __set_temperature(self, temp, unit="c"):
        if unit != "c" and unit != "f":
            raise InvalidConfigValue(f"Unit {unit} is an invalid unit.")

        if type(temp) == float:
            temp = int(temp)

        if type(temp) != int or temp < self.MIN_TEMP or temp > self.MAX_TEMP:
            raise InvalidConfigValue(f"Temperature {temp} is invalid or "
                                     f"not in range ({self.MIN_TEMP} - {self.MAX_TEMP}).")

        self._config["TemUn"] = 1 if unit == "f" else 0
        self._config["SetTem"] = temp

    def __set_fan_speed(self, speed):
        if type(speed) != int or speed < self.MIN_FAN_SPEED or speed > self.MAX_FAN_SPEED:
            raise InvalidConfigValue(f"Speed {speed} is either invalid or "
                                     f"not in range ({self.MIN_FAN_SPEED} - {self.MAX_FAN_SPEED}).")

        self._config["WdSpd"] = speed

    def __set_swing(self, swing):
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

    def __set_bool(self, key, enabled):
        if type(enabled) != bool:
            raise InvalidConfigValue(f"Invalid config value received: {enabled}")

        self._config[key] = int(enabled)