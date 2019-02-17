import os
from binascii import hexlify

from base import LoggingClass
from base.utils import constant_check
from format.pkg.utils import name_codec_map
from utils.keys import PS3_GPKG_KEY, PSP_GPKG_KEY
from utils.utils import DEFAULT_LOCAL_IO_BLOCK_SIZE, read_u32, read_u64, Endianess, decode_data_with_all_codecs, sha1
from .type import EntryType
from ..decryptor import PkgInternalIO


class PKGEntry(LoggingClass):

    def __init__(self, f: PkgInternalIO):
        super().__init__()
        self.f: PkgInternalIO = f

        #: Name offset relative to the header.data_offset value
        self.name_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"Name Offset: {self.name_offset}")

        #: Name size
        self.name_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"Name Size: {self.name_size}")

        #: File offset relative to the header.data_offset value
        self.file_offset: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"File Offset: {self.file_offset}")

        #: File size
        self.file_size: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f"File Size: {self.file_size}")

        # TODO: Use flags or do this better somehow
        #: Read entry flags & type
        entry_flags = read_u32(f, endianess=Endianess.BIG_ENDIAN)

        #: Should this file overwrite a file if it exists
        self.flag_overwrite: bool = (entry_flags >> 24 & 0x80) > 0
        self.logger.debug(f"Overwrite: {self.flag_overwrite}")

        #: Should we use the PSP_GPKG_KEY to decrypt data & name
        self.flag_psp: bool = (entry_flags >> 24 & 0x10) > 0
        self.logger.debug(f"PSP: {self.flag_psp}")

        #: Entry type
        self.type: EntryType = EntryType(entry_flags & 0xFF)
        self.logger.info(f"Type: {self.type}")

        #: Pad to 32 bytes
        self.padding: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        constant_check(self.logger, "Padding", self.padding, valid=0)

        # TODO
        #  It's ugly but I don't have a better solution for now, the only other thing that could be done would be to
        #  read the name data separately from reading the metadata, this gives us a problem with having to take the
        #  is_psp value externally and change it per file so I think this is the best way, period
        #: Data Key, differs from the key used to read the metadata
        self.data_key: bytes
        if self.f.encryption_key == PSP_GPKG_KEY and not self.flag_psp:
            self.data_key = PS3_GPKG_KEY
        else:
            self.data_key = self.f.encryption_key

        #: Seek to the name offset, relative to the header.data_offset value
        f.seek(self.name_offset, PkgInternalIO.SEEK_DATA_OFFSET)
        #: Name data in bytes
        name_data: bytes = f.read(self.name_size, self.data_key)

        try:
            #: File name, including path
            self.name: str = name_data.decode('UTF-8')
        except UnicodeDecodeError as e:
            try:
                #: File name codec fallback
                self.name = name_data.decode(name_codec_map[sha1(name_data)].strip())
            except KeyError:
                #: If all else fails, try all codecs and find a suitable one, add this to naming_exceptions.txt manually
                for codec, string in decode_data_with_all_codecs(name_data):
                    self.logger.error(
                        f'{codec:15}('
                        f'{hexlify(sha1(name_data)).decode().upper()},'
                        f'{codec:15},'
                        f'{name_data.decode(errors="backslashreplace")}'
                        f') -> {string}'
                    )
                raise e
        self.logger.info(f"Name: {self.name}")

    @property
    def is_file(self) -> bool:
        """
        Is this file entry of a file or folder
        :return: True if file else False
        """
        return self.type.is_file

    @staticmethod
    def size():
        return 2 * 4 + 2 * 8 + 4 + 4

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
                    self.f.seek(self.file_offset, PkgInternalIO.SEEK_DATA_OFFSET)

                    bytes_remaining: int = self.file_size
                    while bytes_remaining != 0:
                        to_read: int = block_size if bytes_remaining >= block_size else bytes_remaining
                        bytes_remaining -= export.write(self.f.read(to_read, self.data_key))

                    return True
        else:
            self.logger.info(f'Creating directory: {self.name} -> {path}')
            os.makedirs(path)
            return True
