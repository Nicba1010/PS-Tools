import logging
from io import BytesIO
from typing import IO

from ps.utils import read_u32, Endianess, write_u32
from .constants import magic
from .errors import InvalidSFOException

GAME_ID_SIZE = 0x09

logger = logging.getLogger('SFO Header')


class SFOHeader(object):
    def __init__(self, f: BytesIO):
        #: EDAT magic string, should be: NPD\0
        self.magic: bytes = f.read(4)
        logger.info(f'SFO Magic: {self.magic}')

        if self.magic != magic:
            logger.error('Error, invalid magic')
            raise InvalidSFOException
        else:
            logger.info('Magic Verified')

        version_data: bytes = f.read(4)
        #: SFO file format version
        self.version: str = f'{version_data[0]}.{version_data[1]}{version_data[2]}{version_data[3]}'
        logger.info(f'SFO Version: {self.version}')

        #: Start offset of Key Table
        self.key_table_offset: int = read_u32(f, Endianess.LITTLE_ENDIAN)
        logger.info(f'Key Table Offset: {self.key_table_offset}')

        #: Start offset of Data Table
        self.data_table_offset: int = read_u32(f, Endianess.LITTLE_ENDIAN)
        logger.info(f'Data Table Offset: {self.data_table_offset}')

        #: Entry Count (both tables)
        self.entry_count: int = read_u32(f, Endianess.LITTLE_ENDIAN)
        logger.info(f'Entry Count: {self.entry_count}')

    def write(self, f: IO):
        logger.info('Writing SFO Header Data...')

        #: Write Magic
        f.write(self.magic)

        #: Write File Format Version
        f.write(bytes([int(self.version[0]), int(self.version[2]), int(self.version[3]), int(self.version[4])]))

        #: Write Key Table Offset
        write_u32(f, self.key_table_offset, Endianess.LITTLE_ENDIAN)

        #: Write Data Table Offset
        write_u32(f, self.data_table_offset, Endianess.LITTLE_ENDIAN)

        #: Write Entry Count
        write_u32(f, self.entry_count, Endianess.LITTLE_ENDIAN)

        logger.info('SFO Header Data Written!')
