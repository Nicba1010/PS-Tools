from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hmac, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from utils.keys import SYSCON_MANAGER_KEY

magic: bytes = b'\0\0\0\0PFDB'


def create_syscon_aes_cbc_cipher(iv: bytes) -> Cipher:
    return Cipher(algorithms.AES(SYSCON_MANAGER_KEY), modes.CBC(iv), backend=default_backend())


def hmac_sha256(key: bytes, data: bytes) -> bytes:
    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data)
    return h.finalize()
