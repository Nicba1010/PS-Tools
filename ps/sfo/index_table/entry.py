import logging
from io import BytesIO
from typing import IO

from ps.utils import read_u32, Endianess, read_u16, write_u16, write_u32
from .data_type import DataType

GAME_ID_SIZE = 0x09

logger = logging.getLogger('SFO Index Table Entry')


class IndexTableEntry(object):
    def __init__(self, f: BytesIO):
        #: Key Offset (relative to key_table_offset)
        self.key_offset: int = read_u16(f, Endianess.LITTLE_ENDIAN)
        logger.info(f'Key Offset: {self.key_offset}')

        #: Data Type
        self.data_type: DataType = DataType(f.read(2))
        logger.info(f'Data Type: {self.data_type}')

        #: Data Length (used bytes)
        self.data_length: int = read_u32(f, Endianess.LITTLE_ENDIAN)
        logger.info(f'Data Length: {self.data_length}')

        #: Data Max Length
        self.data_max_length: int = read_u32(f, Endianess.LITTLE_ENDIAN)
        logger.info(f'Data Max Length: {self.data_max_length}')

        #: Data Offset (relative to data_table_offset)
        self.data_offset: int = read_u32(f, Endianess.LITTLE_ENDIAN)
        logger.info(f'Data Offset: {self.data_offset}')

    def write(self, f: IO):
        logger.info('Writing SFO Index Table Entry Data...')

        #: Writing Key Offset
        write_u16(f, self.key_offset, Endianess.LITTLE_ENDIAN)

        #: Writing Data Type
        f.write(self.data_type.value)

        #: Writing Data Length
        write_u32(f, self.data_length, Endianess.LITTLE_ENDIAN)

        #: Writing Data Max Length
        write_u32(f, self.data_max_length, Endianess.LITTLE_ENDIAN)

        #: Writing Data Offset
        write_u32(f, self.data_offset, Endianess.LITTLE_ENDIAN)

        logger.info('SFO Index Table Entry Data Written!')
