from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class AESCipher:
    def __init__(self, key):
        self.cipher = AES.new(key, AES.MODE_ECB)

    def encrypt(self, msg):
        return self.cipher.encrypt(pad(msg, 16))

    def decrypt(self, padded_encrypted_msg):
        return unpad(self.cipher.decrypt(padded_encrypted_msg), 16)