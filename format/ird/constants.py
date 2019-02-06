from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

compressed_magic: bytes = b'\x1F\x8B\x08\x00'

data2_key: bytes = bytes([
    124,
    221,
    14,
    2,
    7,
    110,
    254,
    69,
    153,
    177,
    184,
    44,
    53,
    153,
    25,
    179
])
data2_key_hex: bytes = bytes([
    0x7C, 0xDD, 0x0E, 0x02,
    0x07, 0x6E, 0xFE, 0x45,
    0x99, 0xB1, 0xB8, 0x2C,
    0x35, 0x99, 0x19, 0xB3
])

data2_iv: bytes = bytes([
    34,
    38,
    146,
    141,
    68,
    3,
    47,
    67,
    106,
    253,
    38,
    126,
    116,
    139,
    35,
    147
])

data2_iv_hex: bytes = bytes([
    0x22, 0x26, 0x92, 0x8D,
    0x44, 0x03, 0x2F, 0x43,
    0x6A, 0xFD, 0x26, 0x7E,
    0x74, 0x8B, 0x23, 0x93
])

data2_patch_cipher = Cipher(algorithms.AES(data2_key), modes.CBC(data2_iv), backend=default_backend())
data2_patch_encryptor = data2_patch_cipher.encryptor()
data2_patch_decryptor = data2_patch_cipher.decryptor()
