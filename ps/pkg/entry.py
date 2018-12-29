import os
import struct
from typing import IO

from clint.textui import puts

from ps.utils import DEFAULT_LOCAL_IO_BLOCK_SIZE
from .decryptor import DecryptorIO


class PkgEntry(object):

    def __init__(self, f: 'DecryptorIO'):
        self.f: IO = f
        self.name_offset: int = struct.unpack('>I', f.read(4))[0]
        self.name_size: int = struct.unpack('>I', f.read(4))[0]
        self.file_offset: int = struct.unpack('>Q', f.read(8))[0]
        self.file_size: int = struct.unpack('>Q', f.read(8))[0]
        self.type: int = struct.unpack('>I', f.read(4))[0]
        self.pad: int = struct.unpack('>I', f.read(4))[0]
        puts("Name Offset: {}".format(self.name_offset))
        puts("Name Size: {}".format(self.name_size))
        puts("File Offset: {}".format(self.file_offset))
        puts("File Size: {}".format(self.file_size))
        puts("Type: {}".format(self.type))
        puts("Pad: {}".format(self.pad))

        f.seek(self.name_offset, DecryptorIO.SEEK_DATA_OFFSET)
        # Not decoded to ASCII or UTF8 because some packages even though they are valid, have invalid characters
        self.name: bytes = f.read(self.name_size)
        puts("Name: {}".format(self.name))

    @staticmethod
    def size():
        return 4 * 4 + 2 * 8

    def save_file(self, path: str, block_size: int = DEFAULT_LOCAL_IO_BLOCK_SIZE, use_package_path: bool = False,
                  create_directories: bool = False) -> bool:
        if (os.path.exists(path) and os.path.isdir(path)) or (not os.path.exists(path) and path.endswith(('/', '\\'))):
            if use_package_path:
                path = os.path.join(path, self.name)
            else:
                path = os.path.join(path, os.path.basename(self.name))
        elif os.path.isfile(path):
            pass

        directory = os.path.dirname(path)
        file_name = os.path.basename(path)

        if create_directories and not os.path.exists(directory):
            os.makedirs(directory)

        with open(path, 'wb') as export:
            self.f.seek(self.file_offset, DecryptorIO.SEEK_DATA_OFFSET)
            bytes_remaining: int = self.file_size
            while bytes_remaining != 0:
                to_read: int = block_size if bytes_remaining >= block_size else bytes_remaining
                bytes_remaining -= export.write(self.f.read(to_read))
            return True