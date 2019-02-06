import os
from typing import IO

from clint.textui import puts

from base import LoggingClass
from utils.utils import DEFAULT_LOCAL_IO_BLOCK_SIZE, read_u32, read_u64, Endianess
from .decryptor import DecryptorIO
from .entry_type import EntryType


class PkgEntry(LoggingClass):

    def __init__(self, f: 'DecryptorIO'):
        super().__init__()

        self.f: IO = f
        self.name_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.name_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.file_offset: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.file_size: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        entry_flags = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        # TODO: Use flags or do this better somehow
        self.flag_overwrite: bool = (entry_flags >> 3 & 0x80) > 0
        self.flag_psp: bool = (entry_flags >> 3 & 0x10) > 0
        self.type: EntryType = EntryType(entry_flags & 0xFF)
        self.pad: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        puts(f"Name Offset: {self.name_offset}")
        puts(f"Name Size: {self.name_size}")
        puts(f"File Offset: {self.file_offset}")
        puts(f"File Size: {self.file_size}")
        puts(f"Type: {self.type}")
        puts(f"Overwrite: {self.flag_overwrite}")
        puts(f"PSP: {self.flag_psp}")
        puts(f"Pad: {self.pad}")

        f.seek(self.name_offset, DecryptorIO.SEEK_DATA_OFFSET)
        # Not decoded to ASCII or UTF8 because some packages even though they are valid, have invalid characters
        self.name: str = f.read(self.name_size).decode('UTF-8')
        puts(f"Name: {self.name}")

    @property
    def is_file(self):
        return self.type.is_file

    @staticmethod
    def size():
        return 4 * 4 + 2 * 8

    def save_file(self, path: str, block_size: int = DEFAULT_LOCAL_IO_BLOCK_SIZE, use_package_path: bool = False,
                  create_directories: bool = True) -> bool:
        if (os.path.exists(path) and os.path.isdir(path)) or (not os.path.exists(path) and path.endswith(('/', '\\'))):
            if use_package_path:
                path = os.path.join(path, self.name)
            else:
                path = os.path.join(path, os.path.basename(self.name))
        elif os.path.isfile(path):
            pass

        directory: str = os.path.dirname(path)
        # TODO: Do we really need this? Maybe for logging?
        # file_name: str = os.path.basename(path)

        if create_directories and not os.path.exists(directory):
            os.makedirs(directory)

        if self.is_file:
            puts(f'Extracting file: {self.name} -> {path}')
            if not os.path.exists(path) or self.flag_overwrite:
                with open(path, 'wb') as export:
                    self.f.seek(self.file_offset, DecryptorIO.SEEK_DATA_OFFSET)
                    bytes_remaining: int = self.file_size
                    while bytes_remaining != 0:
                        to_read: int = block_size if bytes_remaining >= block_size else bytes_remaining
                        bytes_remaining -= export.write(self.f.read(to_read))
                    return True
        else:
            puts(f'Creating directory: {self.name} -> {path}')
            os.makedirs(path)
            return True
