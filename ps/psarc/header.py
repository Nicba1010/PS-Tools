from typing import IO

from aenum import Enum
from clint.textui import puts

from ps.utils import read_u32, read_u16, Endianess
from .errors import InvalidPSARCError

magic: bytes = b'PSAR'


class CompressionType(Enum):
    ZLIB = b'zlib'
    LZMA = b'lzma'


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

        self.version_major: int = read_u16(f, endianess=Endianess.LITTLE_ENDIAN)
        self.version_minor: int = read_u16(f, endianess=Endianess.LITTLE_ENDIAN)
        puts("Version: v{}.{}".format(self.version_major, self.version_minor))

        self.compression_type: CompressionType = CompressionType(f.read(4))
        puts("Compression Type: {}".format(self.compression_type))

        self.toc_length: int = read_u32(f, endianess=Endianess.LITTLE_ENDIAN)
        self.toc_entry_size: int = read_u32(f, endianess=Endianess.LITTLE_ENDIAN)
        self.toc_entries: int = read_u32(f, endianess=Endianess.LITTLE_ENDIAN)
        self.block_size: int = read_u32(f, endianess=Endianess.LITTLE_ENDIAN)
        self.archive_path_type: ArchivePathType = ArchivePathType(read_u32(f, endianess=Endianess.LITTLE_ENDIAN))
        puts("TOC Length: {}".format(self.toc_length))
        puts("TOC Entry Size: {}".format(self.toc_entry_size))
        puts("TOC Entries: {}".format(self.toc_entries))
        puts("Block Size: {}".format(self.block_size))
        puts("Archive Path Type: {}".format(self.archive_path_type))
