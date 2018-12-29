import struct
from binascii import hexlify
from typing import IO

from clint.textui import puts
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes

from .errors import InvalidPKGException
from .revision import PkgRevision
from .type import PkgType
from ..utils import ps3_aes_key, psp_aes_key

backend = default_backend()
magic: bytes = b'\x7fPKG'


class PkgHeader(object):
    def __init__(self, f: IO):
        self.magic: bytes = f.read(4)
        print("PKG Magic: {}".format(self.magic))

        if self.magic != magic:
            raise InvalidPKGException
        else:
            puts("Magic Verified")

        self.revision: PkgRevision = PkgRevision(f.read(2))
        self.type: PkgType = PkgType(f.read(2))
        puts("PKG Revision: {}".format(self.revision))
        puts("PKG Type: {}".format(self.type))

        self.cipher = Cipher(algorithms.AES(
            ps3_aes_key if self.type == PkgType.PS3 else psp_aes_key
        ), modes.ECB(), backend=backend)
        self.encryptor = self.cipher.encryptor()
        puts("Encrypter initialized...")

        self.metadata_offset: int = struct.unpack('>I', f.read(4))[0]
        self.metadata_count: int = struct.unpack('>I', f.read(4))[0]
        self.metadata_size: int = struct.unpack('>I', f.read(4))[0]
        puts("Metadata Offset: {}".format(self.metadata_offset))
        puts("Metadata Count: {}".format(self.metadata_count))
        puts("Metadata Size: {}".format(self.metadata_size))

        self.item_count: int = struct.unpack('>I', f.read(4))[0]
        puts("Item Count: {}".format(self.item_count))

        self.total_size: int = struct.unpack('>Q', f.read(8))[0]
        self.data_offset: int = struct.unpack('>Q', f.read(8))[0]
        self.data_size: int = struct.unpack('>Q', f.read(8))[0]
        puts("Total Size: {}".format(self.total_size))
        puts("Data Offset: {}".format(self.data_offset))
        puts("Data Size: {}".format(self.data_size))

        self.content_id: str = f.read(0x24).decode('utf-8')
        puts("Content ID: {}".format(self.content_id))

        self.padding: bytes = f.read(0x0C)

        self.digest: bytes = f.read(0x10)
        self.pkg_data_riv: bytes = f.read(0x10)
        self.header_cmac_hash: bytes = f.read(0x10)
        self.header_npdrm_signature: bytes = f.read(0x28)
        self.header_sha1_hash: bytes = f.read(0x08)
        puts("Digest: {}".format(hexlify(self.digest)))
        puts("PKG Data Riv: {}".format(self.pkg_data_riv))
        puts("Header CMAC Hash: {}".format(hexlify(self.header_cmac_hash)))
        puts("Header NPDRM Signature: {}".format(hexlify(self.header_npdrm_signature)))
        puts("Header SHA1 Hash: {}".format(hexlify(self.header_sha1_hash)))
