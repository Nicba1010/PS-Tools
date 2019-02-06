import logging
from typing import IO

from ps.utils import read_u32, read_u16, Endianess
from .compression_type import CompressionType
from .constants import magic
from .errors import InvalidPSARCMagicException
from .path_type import ArchivePathType

logger = logging.getLogger('PSARC Header')


class PSARCHeader(object):
    def __init__(self, f: IO):
        #: PSARC Magic String (should ne PSAR)
        self.magic: bytes = f.read(4)
        logger.info(f'PSARC Magic: {self.magic}')

        if self.magic != magic:
            raise InvalidPSARCMagicException
        else:
            logger.info('Magic Verified')

        #: PSARC Minor and Major File Versions
        self.version_major: int = read_u16(f, endianess=Endianess.BIG_ENDIAN)
        self.version_minor: int = read_u16(f, endianess=Endianess.BIG_ENDIAN)
        logger.info(f'Version: v{self.version_major}.{self.version_minor}')

        #: PSARC Compression Type
        self.compression_type: CompressionType = CompressionType(f.read(4))
        logger.info(f'Compression Type: {self.compression_type}')

        #: PSARC TOC Length
        self.toc_length: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        logger.info(f'TOC Length: {self.toc_length}')

        #: PSARC TOC Entry Size
        self.toc_entry_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        logger.info(f'TOC Entry Size: {self.toc_entry_size}')

        #: PSARC TOC Entry Count
        self.toc_entry_count: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        logger.info(f'TOC Entries: {self.toc_entry_count}')

        #: PSARC Block Size
        self.block_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        logger.info(f'Block Size: {self.block_size}')

        #: PSARC Archive Path Type
        # TODO: Fucking use this actually
        self.archive_path_type: ArchivePathType = ArchivePathType(read_u32(f, endianess=Endianess.BIG_ENDIAN))
        logger.info(f'Archive Path Type: {self.archive_path_type}')
