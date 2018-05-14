from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class AESCipher:
    BLOCK_SIZE = 16

    def __init__(self, key):
        self.cipher = AES.new(key, AES.MODE_ECB)

    def encrypt(self, msg):
        return self.cipher.encrypt(pad(msg, self.BLOCK_SIZE))

    def decrypt(self, msg):
        return unpad(self.cipher.decrypt(msg), self.BLOCK_SIZE)