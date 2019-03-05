from __future__ import annotations

import os
from binascii import hexlify

from base import LoggingClass
from base.utils import constant_check
from ..utils import name_codec_map
from utils.keys import PS3_GPKG_KEY, PSP_GPKG_KEY
from utils.utils import DEFAULT_LOCAL_IO_BLOCK_SIZE, read_u32, read_u64, Endianess, decode_data_with_all_codecs, sha1
from .type import EntryType
from ..decryptor import PkgInternalIO


class PkgEntry(LoggingClass):
    def __init__(self):
        """
        Init
        """
        super().__init__()

        self.name_offset: int = 0
        """Name offset relative to the :attr:`~format.pkg.header.PkgHeader.data_offset` value"""

        self.name_size: int = 0
        """Name size in bytes"""

        self.file_offset: int = 0
        """File offset relative to the :attr:`~format.pkg.header.PkgHeader.data_offset` value"""

        self.file_size: int = 0
        """File size in bytes"""

        self.overwrite: bool = False
        """Should this entry overwrite an already existing file"""

        self.is_psp: bool = False
        """Is this a PSP entry - i.e. should we use :attr:`~utils.keys.PSP_GPKG_KEY` to decrypt it"""

        self.entry_type: EntryType = EntryType.REGULAR
        """Entry type"""

        self.padding: int = 0
        """Padding to align the file to 32 bytes, always 0"""

        self.name: str = ""
        """File name, including path encoded using :attr:`name_codec`"""

        self.name_codec: str = "UTF-8"
        """File name codec, should be UTF-8 but there are exceptions"""

        self.__data_key: bytes = None
        """Data encryption key, do not change this unless critically needed"""

    @staticmethod
    def read_from_file(f: PkgInternalIO) -> PkgEntry:
        """
        Reads data into the entry from the file

        Args:
            f: file handle

        Returns:
            constructed PkgEntry
        """
        #: Initialize entry
        entry: PkgEntry = PkgEntry()

        entry.name_offset = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        entry.logger.debug(f"Name Offset: {entry.name_offset}")

        entry.name_size = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        entry.logger.debug(f"Name Size: {entry.name_size}")

        entry.file_offset = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        entry.logger.debug(f"File Offset: {entry.file_offset}")

        entry.file_size = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        entry.logger.info(f"File Size: {entry.file_size}")

        # TODO: Use flags or do this better somehow
        #: Read entry flags & type
        entry_flags = read_u32(f, endianess=Endianess.BIG_ENDIAN)

        entry.overwrite = (entry_flags >> 24 & 0x80) > 0
        entry.logger.debug(f"Overwrite: {entry.overwrite}")

        #: Should we use the PSP_GPKG_KEY to decrypt data & name
        entry.is_psp = (entry_flags >> 24 & 0x10) > 0
        entry.logger.debug(f"PSP: {entry.is_psp}")

        #: Entry type
        entry.entry_type = EntryType(entry_flags & 0xFF)
        entry.logger.info(f"Entry Type: {entry.entry_type}")

        #: Pad to 32 bytes
        entry.padding = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        constant_check(entry.logger, "Padding", entry.padding, valid=0)

        # TODO
        #  It's ugly but I don't have a better solution for now, the only other thing that could be done would be to
        #  read the name data separately from reading the metadata, this gives us a problem with having to take the
        #  is_psp value externally and change it per file so I think this is the best way, period
        if f.encryption_key == PSP_GPKG_KEY and not entry.is_psp:
            entry.__data_key = PS3_GPKG_KEY
        else:
            entry.__data_key = f.encryption_key

        #: Seek to the name offset, relative to the header.data_offset value
        f.seek(entry.name_offset, PkgInternalIO.SEEK_DATA_OFFSET)
        #: Name data in bytes
        name_data: bytes = f.read(entry.name_size, entry.data_key)

        try:
            #: File name, including path
            entry.name: str = name_data.decode('UTF-8')
        except UnicodeDecodeError as e:
            try:
                #: File name codec fallback
                entry.name = name_data.decode(name_codec_map[sha1(name_data)].strip())
            except KeyError:
                #: If all else fails, try all codecs and find a suitable one, add this to naming_exceptions.txt manually
                for codec, string in decode_data_with_all_codecs(name_data):
                    entry.logger.error(
                        f'{codec:15}('
                        f'{hexlify(sha1(name_data)).decode().upper()},'
                        f'{codec:15},'
                        f'{name_data.decode(errors="backslashreplace")}'
                        f') -> {string}'
                    )
                raise e
        entry.logger.info(f"Name: {entry.name}")

        return entry

    @property
    def data_key(self) -> bytes:
        """
        Data Key, differs from the key used to read the metadata

        Returns:
            :attr:`__data_key`
        """
        return self.__data_key

    @property
    def is_file(self) -> bool:
        """
        Is this file entry of a file or folder

        Returns: True if this file is a folder, otherwise False

        """
        return self.entry_type.is_file

    @staticmethod
    def size():
        """
        Size of a file entry structure in bytes.
        Excluding :attr:`name` since it is written in the data portion

        Returns:
            Size of a file entry structure in bytes
        """
        return 32

    def export(self, f: PkgInternalIO, path: str, block_size: int = DEFAULT_LOCAL_IO_BLOCK_SIZE,
               use_package_path: bool = False, create_directories: bool = True) -> bool:
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
            if not os.path.exists(path) or self.overwrite:
                with open(path, 'wb') as export:
                    f.seek(self.file_offset, PkgInternalIO.SEEK_DATA_OFFSET)

                    bytes_remaining: int = self.file_size
                    while bytes_remaining != 0:
                        to_read: int = block_size if bytes_remaining >= block_size else bytes_remaining
                        bytes_remaining -= export.write(f.read(to_read, self.data_key))

                    return True
        else:
            self.logger.info(f'Creating directory: {self.name} -> {path}')
            os.makedirs(path)
            return True
