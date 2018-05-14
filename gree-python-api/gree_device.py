import socket
import base64
import json


class GreeDevice():
    GENERIC_AES_KEY = b"a3K8Bx%2r8Y7#xDh"
    SCAN_PACKET = b'{"t": "scan"}'

    def __init__(self, mac, unique_key, host='255.255.255.255', port=7000, timeout=15):
        if ':' in mac:
            mac = mac.replace(':', '')
        self._mac = mac
        self._unique_key = unique_key
        self._host = host
        self._port = port

        self._unique_cipher = AESCipher(self._unique_key)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._sock.settimeout(timeout)

        self._status = None

        self._config = GreeConfig()

    def _encrypt_pack(self, json_pack):
        bytestring = str.encode(json.dumps(json_pack))
        return base64.b64encode(self._unique_key.encrypt(bytestring))

    def _generate_status_packet(self):
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
        pack['mac'] = self._mac

        encrypted_pack = self._encrypt_pack(pack)

        packet = json.loads("""{
            "cid": "app",
            "i": 0,
            "pack": "<encrypted, encoded pack>",
            "t": "pack",
            "tcid": "<MAC address>",
            "uid": 0
        }""")
        packet['pack'] = encrypted_pack.decode('utf-8')
        packet['tcid'] = self._mac

        return packet

    def _send_json(self, json_packet):
        return self._sock.sendto(json.dumps(json_packet), (self._host, self._port)) > 0

    def _recv_response(self):
        response = ''
        while True:
            data = self._sock.recvfrom(1024)[0]
            if not data:
                break
            response += data

        return json.loads(response)

    def _parse_response(self, response, cipher=None):
        cipher = cipher or self._unique_cipher
        if type(cipher) is not AESCipher:
            raise InvalidParameterGiven("[_parse_response]: Param cipher is not of type AESCipher")

        if 'pack' not in response:
            raise InvalidResponse("[_parse_response]: Response object has no 'pack' field")

        pack = response['pack']
        decoded_pack = base64.b64decode(pack)
        decrypted_pack = json.loads(cipher.decrypt(decoded_pack))

        response['pack'] = decrypted_pack

        return response

    def update_status(self):
        status_packet = self._generate_status_packet()

        if self._send_json(status_packet):
            response = self._recv_response()
            parsed_response = self._parse_response(response)

            status = {}
            keys = parsed_response['pack']['cols']
            values = parsed_response['pack']['dat']

            for i in range(keys):
                status[keys[i]] = values[i]

            self._status = status
            return True
        return False

    def send_command(self, **kwargs):
        for key, func in self._config._config_mapping.items():
            if key in kwargs:
                func(kwargs[key])

        # TODO: generate packet

    @property
    def status(self):
        if not self._status:
            self.update_status()
        return self._status