from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

import base64


class AESCipher:
    def __init__(self):
        self.bs = 16
        self.pad = lambda s: bytes(s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs), 'utf-8')
        self.unpad = lambda s: s[0:-ord(s[-1:])]
        self.iv = bytes([0x00] * 16)

    def encrypt(self, key, raw):
        set_key = key.encode('utf-8')
        # raw = pad(bytes(raw), AES.block_size)
        cipher = AES.new(set_key, AES.MODE_CBC, IV=self.iv)
        ct_bytes = cipher.encrypt(pad(bytes(raw, encoding="utf-8"), self.bs))

        encrypt = base64.b64encode(ct_bytes).decode('utf-8')
        return encrypt

    def decrypt(self, key, enc):
        get_key = key
        set_key = get_key.encode('utf-8')

        ct = base64.b64decode(enc)

        cipher = AES.new(set_key, AES.MODE_CBC, IV=self.iv)
        unpad_text = unpad(cipher.decrypt(ct), AES.block_size)

        return unpad_text.decode('utf-8')
