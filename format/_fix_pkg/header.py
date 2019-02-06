from binascii import hexlify
from typing import IO

from clint.textui import puts
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes

from base.header import MagicFileHeader
from utils.utils import ps3_aes_key, psp_aes_key, read_u32, read_u64, Endianess
from .revision import PkgRevision
from .type import PkgType

backend = default_backend()


class PkgHeader(MagicFileHeader):
    def __init__(self, f: IO):
        super().__init__(f)

        self.revision: PkgRevision = PkgRevision(f.read(2))
        self.type: PkgType = PkgType(f.read(2))
        puts("PKG Revision: {}".format(self.revision))
        puts("PKG Type: {}".format(self.type))

        self.cipher = Cipher(algorithms.AES(
            ps3_aes_key if self.type == PkgType.PS3 else psp_aes_key
        ), modes.ECB(), backend=backend)
        self.encryptor = self.cipher.encryptor()
        puts("Encryptor initialized...")

        self.metadata_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.metadata_count: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.metadata_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        puts("Metadata Offset: {}".format(self.metadata_offset))
        puts("Metadata Count: {}".format(self.metadata_count))
        puts("Metadata Size: {}".format(self.metadata_size))

        self.item_count: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        puts("Item Count: {}".format(self.item_count))

        self.total_size: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.data_offset: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.data_size: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
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

    @property
    def magic(self) -> bytes:
        return b'\x7fPKG'
