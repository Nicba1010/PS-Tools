import struct
from typing import IO, List

from clint.textui import indent, puts

from .header import PSARCHeader


class TOCEntry(object):
    def __init__(self, f: IO):
        self.hash: bytes = f.read(16)
        self.block_index: int = read_u32(f)
        self.uncompressed_size: int = struct.unpack('>Q', bytes([0, 0, 0]) + f.read(5))[0]
        self.offset: int = struct.unpack('>Q', bytes([0, 0, 0]) + f.read(5))[0]
        puts("Hash: {}".format(self.hash))
        puts("Block Index: {}".format(self.block_index))
        puts("Uncompressed Size: {}".format(self.uncompressed_size))
        puts("Offset: {}".format(self.offset))


class PSARC(object):
    def __init__(self, path: str):
        self.path: str = path
        with open(self.path, 'rb') as f:
            self.header: PSARCHeader = PSARCHeader(f)

            self.entries: List[TOCEntry] = []
            for i in range(0, self.header.toc_entries):
                with indent(4, '>>>'):
                    self.entries.append(TOCEntry(f))
