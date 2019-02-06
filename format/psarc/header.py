from typing import IO

from base.header import MagicFileHeader
from utils.utils import read_u32, read_u16, Endianess
from .compression_type import CompressionType
from .path_type import ArchivePathType


class PSARCHeader(MagicFileHeader):
    def __init__(self, f: IO):
        super().__init__(f)

        #: PSARC Minor and Major File Versions
        self.version_major: int = read_u16(f, endianess=Endianess.BIG_ENDIAN)
        self.version_minor: int = read_u16(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Version: v{self.version_major}.{self.version_minor}')

        #: PSARC Compression Type
        self.compression_type: CompressionType = CompressionType(f.read(4))
        self.logger.info(f'Compression Type: {self.compression_type}')

        #: PSARC TOC Length
        self.toc_length: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'TOC Length: {self.toc_length}')

        #: PSARC TOC Entry Size
        self.toc_entry_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'TOC Entry Size: {self.toc_entry_size}')

        #: PSARC TOC Entry Count
        self.toc_entry_count: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'TOC Entries: {self.toc_entry_count}')

        #: PSARC Block Size
        self.block_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Block Size: {self.block_size}')

        #: PSARC Archive Path Type
        # TODO: Fucking use this actually
        self.archive_path_type: ArchivePathType = ArchivePathType(read_u32(f, endianess=Endianess.BIG_ENDIAN))
        self.logger.info(f'Archive Path Type: {self.archive_path_type}')

    @property
    def magic(self) -> bytes:
        return b'PSAR'
