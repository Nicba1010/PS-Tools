import os
from binascii import hexlify
from typing import IO

from base import LoggingClass
from format.pkg.decryptor import DecryptorIO
from format.pkg.utils import name_codec_map
from utils.utils import DEFAULT_LOCAL_IO_BLOCK_SIZE, read_u32, read_u64, Endianess, decode_data_with_all_codecs, sha1
from .type import EntryType


class PKGEntry(LoggingClass):

    def __init__(self, f: DecryptorIO):
        super().__init__()
        self.f: IO = f

        self.name_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"Name Offset: {self.name_offset}")

        self.name_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"Name Size: {self.name_size}")

        self.file_offset: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"File Offset: {self.file_offset}")

        self.file_size: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f"File Size: {self.file_size}")

        entry_flags = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        # TODO: Use flags or do this better somehow
        self.flag_overwrite: bool = (entry_flags >> 3 & 0x80) > 0
        self.logger.debug(f"Overwrite: {self.flag_overwrite}")

        self.flag_psp: bool = (entry_flags >> 3 & 0x10) > 0
        self.logger.debug(f"PSP: {self.flag_psp}")
        try:
            self.type: EntryType = EntryType(entry_flags & 0xFF)
            self.logger.info(f"Type: {self.type}")
        except:
            pass
        self.pad: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"Pad: {self.pad}")

        f.seek(self.name_offset, DecryptorIO.SEEK_DATA_OFFSET)
        # TODO: ugh encoding
        name_data: bytes = f.read(self.name_size)
        try:
            self.name: str = name_data.decode('UTF-8')
        except UnicodeDecodeError as e:
            try:
                self.name = name_data.decode(name_codec_map[sha1(name_data)])
            except KeyError:
                for codec, string in decode_data_with_all_codecs(name_data):
                    print(f'{codec:15}({name_data}) ({hexlify(sha1(name_data)).decode("ASCII").upper()}) -> {string}')
                raise e
        self.logger.info(f"Name: {self.name}")

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
            self.logger.info(f'Extracting file: {self.name} -> {path}')
            if not os.path.exists(path) or self.flag_overwrite:
                with open(path, 'wb') as export:
                    self.f.seek(self.file_offset, DecryptorIO.SEEK_DATA_OFFSET)
                    bytes_remaining: int = self.file_size
                    while bytes_remaining != 0:
                        to_read: int = block_size if bytes_remaining >= block_size else bytes_remaining
                        bytes_remaining -= export.write(self.f.read(to_read))
                    return True
        else:
            self.logger.info(f'Creating directory: {self.name} -> {path}')
            os.makedirs(path)
            return True
