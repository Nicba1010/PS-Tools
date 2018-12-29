import struct
from typing import IO

from aenum import Enum
from clint.textui import puts

from .errors import InvalidPSARCError

magic: bytes = b'PSAR'


class CompressionType(Enum):
    ZLIB = b'zlib'
    LZMA = b'lzmax'


class ArchivePathType(Enum):
    RELATIVE = 0x00
    IGNORE_CASE = 0x01
    ABSOLUTE = 0x02


class PSARCHeader(object):
    def __init__(self, f: IO):
        self.magic: bytes = f.read(4)
        print("PSARC Magic: {}".format(self.magic))

        if self.magic != magic:
            raise InvalidPSARCError
        else:
            puts("Magic Verified")

        self.version_major: int = struct.unpack('>H', f.read(2))[0]
        self.version_minor: int = struct.unpack('>H', f.read(2))[0]
        puts("Version: v{}.{}".format(self.version_major, self.version_minor))

        self.compression_type: CompressionType = CompressionType(f.read(4))
        puts("Compression Type: {}".format(self.compression_type))

        self.toc_length: int = struct.unpack('>I', f.read(4))[0]
        self.toc_entry_size: int = struct.unpack('>I', f.read(4))[0]
        self.toc_entries: int = struct.unpack('>I', f.read(4))[0]
        self.block_size: int = struct.unpack('>I', f.read(4))[0]
        self.archive_path_type: ArchivePathType = ArchivePathType(struct.unpack('>I', f.read(4))[0])
        puts("TOC Length: {}".format(self.toc_length))
        puts("TOC Entry Size: {}".format(self.toc_entry_size))
        puts("TOC Entries: {}".format(self.toc_entries))
        puts("Block Size: {}".format(self.block_size))
        puts("Archive Path Type: {}".format(self.archive_path_type))