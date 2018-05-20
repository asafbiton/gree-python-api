import socket
import base64
import json
import threading

from .gree_config import GreeConfig
from .aes_cipher import AESCipher
from .exceptions import InvalidParameterGiven, InvalidResponse, UnexpectedResponse


class GreeDevice():
    GENERIC_AES_KEY = b'a3K8Bx%2r8Y7#xDh'
    SCAN_PACKET = b'{"t": "scan"}'

    def __init__(self, mac, unique_key, host='255.255.255.255', port=7000, timeout=15):
        if ':' in mac:
            mac = mac.replace(':', '')
        self.__mac = mac
        self.__unique_key = unique_key
        self.__host = host
        self.__port = port

        self.__unique_cipher = AESCipher(self.__unique_key)

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.__sock.settimeout(timeout)

        self.__status = None

        self.__lock = threading.Lock()

    def __encrypt_pack(self, json_pack):
        bytestring = str.encode(json.dumps(json_pack))
        return base64.b64encode(self.__unique_cipher.encrypt(bytestring))

    def __generate_status_packet(self):
        pack = json.loads("""
        {
          "cols": [
            "Pow", 
            "Mod", 
            "SetTem", 
            "WdSpd", 
            "Air", 
            "Blo", 
            "Health", 
            "SwhSlp", 
            "Lig", 
            "SwingLfRig", 
            "SwUpDn", 
            "Quiet", 
            "Tur", 
            "StHt", 
            "TemUn", 
            "HeatCoolType", 
            "TemRec", 
            "SvSt"
          ],
          "mac": "<MAC address>",
          "t": "status"
        }
        """)
        pack['mac'] = self.__mac

        encrypted_pack = self.__encrypt_pack(pack)

        packet = json.loads("""{
            "cid": "app",
            "i": 0,
            "pack": "<encrypted, encoded pack>",
            "t": "pack",
            "tcid": "<MAC address>",
            "uid": 0
        }""")
        packet['pack'] = encrypted_pack.decode('utf-8')
        packet['tcid'] = self.__mac

        return packet

    def __send_json(self, json_packet):
        bytes_sent = 0

        with self.__lock:
            bytes_sent = self.__sock.sendto(json.dumps(json_packet).encode('utf-8'), 
                                            (self.__host, self.__port))

        return bytes_sent > 0

    def __recv_response(self):
        with self.__lock:
            response = self.__sock.recvfrom(1024)[0]

        return json.loads(response.decode('utf-8'))

    def __parse_response(self, response, cipher=None):
        cipher = cipher or self.__unique_cipher
        if type(cipher) is not AESCipher:
            raise InvalidParameterGiven("[_parse_response]: Param cipher is not of type AESCipher")

        if 'pack' not in response:
            raise InvalidResponse("[_parse_response]: Response object has no 'pack' field")

        pack = response['pack']
        decoded_pack = base64.b64decode(pack)
        decrypted_pack = json.loads(cipher.decrypt(decoded_pack))

        response['pack'] = decrypted_pack

        return response

    def __generate_cmd_packet(self, config):
        pack = json.loads("""{
          "opt": ["TemUn", "SetTem"],
          "p": [0, 27],
          "t": "cmd"
        }""")
        pack['opt'] = list(config.config.keys())
        pack['p'] = list(config.config.values())

        encrypted_pack = self.__encrypt_pack(pack)

        packet = json.loads("""{
          "cid": "app",
          "i": 0,
          "pack": "<encrypted, encoded pack>",
          "t": "pack",
          "tcid": "<MAC address>",
          "uid": 0
        }""")
        packet['pack'] = encrypted_pack.decode('utf-8')
        packet['tcid'] = self.__mac

        return packet

    def update_status(self):
        status_packet = self.__generate_status_packet()

        if self.__send_json(status_packet):
            response = self.__recv_response()
            parsed_response = self.__parse_response(response)

            status = {}
            keys = parsed_response['pack']['cols']
            values = parsed_response['pack']['dat']

            for i in range(len(keys)):
                status[keys[i]] = values[i]

            self.__status = status
            return True
        return False

    def send_command(self, power_on=None, temperature=None, mode=None,
                     is_quiet=None, fan_speed=None, swing=None,
                     energy_saving=None, display_on=None, health_mode=None,
                     air_valve=None, blow_mode=None, turbo_mode=None):
        """
        :param power_on: bool
        :param temperature: int
        :param mode: int (GreeConfig.MODES)
        :param is_quiet: bool
        :param fan_speed: int (0-5)
        :param swing: int (0-11)
        :param energy_saving: bool
        :param display_on: bool
        :param health_mode: bool
        :param air_valve: bool
        :param blow_mode: bool
        :param turbo_mode: bool
        :return:
        """

        config = GreeConfig()
        if power_on is not None:        config.power_on = power_on
        if temperature is not None:     config.temperature = temperature
        if mode is not None:            config.mode = mode
        if fan_speed is not None:       config.fan_speed = fan_speed
        if swing is not None:           config.swing = swing
        if is_quiet is not None:        config.quiet_mode_enabled = is_quiet
        if energy_saving is not None:   config.energy_saving_enabled = energy_saving
        if display_on is not None:      config.display_enabled = display_on
        if health_mode is not None:     config.health_mode_enabled = health_mode
        if air_valve is not None:       config.air_valve_enabled = air_valve
        if blow_mode is not None:       config.blow_mode_enabled = blow_mode
        if turbo_mode is not None:      config.turbo_mode_enabled = turbo_mode

        cmd_packet = self.__generate_cmd_packet(config)

        if self.__send_json(cmd_packet):
            response = self.__recv_response()
            parsed_response = self.__parse_response(response)

            if parsed_response['pack']['r'] != 200:
                raise UnexpectedResponse(f"Pack parameter 'r' is different than expected "
                                         f"(received {parsed_response['pack']['r']}, expected 200). "
                                         f"This may mean an error has occured.")

            return True
        return False

    @property
    def status(self):
        if not self.__status:
            self.update_status()
        return self.__status