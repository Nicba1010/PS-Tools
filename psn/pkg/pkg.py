import hashlib
import struct
from binascii import hexlify

from aenum import Enum
from clint.textui import puts, indent
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from psn.pkg.metadata import PkgMetadata
from .content_type import ContentType
from .drm_type import DrmType
from .errors import InvalidPkgError

magic: bytearray = bytes([0x7F, 0x50, 0x4B, 0x47])
backend = default_backend()
ps3_aes_key: bytes = bytes([
    0x2e, 0x7b, 0x71, 0xd7, 0xc9, 0xc9, 0xa1, 0x4e, 0xa3, 0x22, 0x1f, 0x18, 0x88, 0x28, 0xb8, 0xf8
])

class PkgRevision(Enum):
    RETAIL = bytes([0x80, 0x00])
    DEBUG = bytes([0x00, 0x00])


class PkgType(Enum):
    PS3 = bytes([0x00, 0x01])
    PSP_PSVITA = bytes([0x00, 0x02])


class Pkg(object):
    cipher: Cipher = Cipher(algorithms.AES(ps3_aes_key), modes.ECB(), backend=backend)
    decryptor = cipher.decryptor()

    def __init__(self, path: str):
        self.path: str = path
        with open(self.path, 'rb') as f:
            self.magic: bytes = f.read(4)
            print("PKG Magic: {}".format(self.magic))

            if self.magic != magic:
                raise InvalidPkgError
            else:
                puts("Magic Verified")

            self.revision: PkgRevision = PkgRevision(f.read(2))
            self.type: PkgType = PkgType(f.read(2))
            puts("PKG Revision: {}".format(self.revision))
            puts("PKG Type: {}".format(self.type))

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
            puts("PKG Data Riv: {}".format(hexlify(self.pkg_data_riv)))
            puts("Header CMAC Hash: {}".format(hexlify(self.header_cmac_hash)))
            puts("Header NPDRM Signature: {}".format(hexlify(self.header_npdrm_signature)))
            puts("Header SHA1 Hash: {}".format(hexlify(self.header_sha1_hash)))

            sha1 = hashlib.sha1()
            f.seek(0x00)
            sha1.update(f.read(0x80))
            if sha1.digest()[-8:] != self.header_sha1_hash:
                raise InvalidPkgError
            else:
                puts("Header SHA1 Hash Verified!")

            self.drm_type: DrmType = None
            self.content_type: ContentType = None
            self.system_version: str = None
            self.app_version: str = None
            self.package_version: str = None
            self.make_package_npdrm_rev: int = None
            self.title_id: str = None
            self.qa_digest: bytes = None

            f.seek(self.metadata_offset)

            for metadata_index in range(0, self.metadata_count):
                puts("Processing metadata on index {}:".format(metadata_index))
                with indent(4, '>>>'):
                    metadata: PkgMetadata = PkgMetadata.create(f)

            puts(str(f.tell()))

            f.seek(self.data_offset)
            with open('test.bin', 'wb') as w:
                w.write(f.read(self.data_size))
