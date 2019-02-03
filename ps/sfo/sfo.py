import logging
import os
from collections import OrderedDict
from io import BytesIO
from typing import List, Union, Dict, Optional

from ps.sfo.index_table import DataType
from ps.utils import read_string_null_terminated, read_i32, write_string_null_terminated, write_i32, Endianess
from .errors import EmptySFOException
from .header import SFOHeader
from .index_table import IndexTableEntry

logger = logging.getLogger('SFO')


class SFO(object):
    def __init__(self, path: str):
        #: File Path
        self.path: str = path

        logger.info(f"Parsing file: {self.path}")

        if os.stat(self.path).st_size == 0:
            logger.error("Error, file is empty")
            raise EmptySFOException()

        self.file_handle: BytesIO = open(self.path, 'rb')

        #: File Header
        self.header: SFOHeader = SFOHeader(self.file_handle)

        #: Index Table
        self.index_table: List[IndexTableEntry] = list()
        for i in range(0, self.header.entry_count):
            logger.info(f'Reading SFO Index Table Entry #{i}')
            self.index_table.append(IndexTableEntry(self.file_handle))

        #: Alignment Padding to int32
        self.file_handle.seek(self.file_handle.tell() % 4, os.SEEK_CUR)

        #: Key Table
        self.key_data_map: Dict[str, Union[str, int]] = OrderedDict()
        for entry in self.index_table:
            #: Index Table Entry Index
            index: int = self.index_table.index(entry)

            #: Seek to entry key offset
            self.file_handle.seek(self.header.key_table_offset + entry.key_offset)

            #: Read Key Name (Always UTF-8, NULL Terminated, [A-Z])
            key: str = read_string_null_terminated(self.file_handle, encoding='UTF-8')

            #: Seek to entry data offset
            self.file_handle.seek(self.header.data_table_offset + entry.data_offset)

            #: Data (string(NULL/!NULL Terminated) / int)
            data: Union[str, int] = None
            if entry.data_type == DataType.INT32:
                data = read_i32(self.file_handle, endianess=Endianess.LITTLE_ENDIAN)
            elif entry.data_type == DataType.UTF8:
                data = read_string_null_terminated(self.file_handle, encoding='UTF-8')
            elif entry.data_type == DataType.UTF8_SPECIAL:
                data = self.file_handle.read(entry.data_length).decode(encoding='UTF-8')

            logger.info(
                f'Key Data Map Entry #{index} ({entry.data_length}/{entry.data_max_length}): '
                f'{key[:-1]} ({entry.data_type}) -> {data}'
            )
            self.key_data_map[key] = data

    def set_data(self, key: str, data: Union[str, int]):
        if key not in self.key_data_map:
            logger.error(f'Key {key} does not exist in the key table...')
        else:
            #: Index Table Entry Index
            index: int = list(self.key_data_map.keys()).index(key)

            #: Index Table Entry
            index_table_entry = self.index_table[index]

            #: Index Table Entry Data Type
            data_type: DataType = index_table_entry.data_type

            #: Check if entered data can be parsed to an integer
            try:
                int(data)
                can_data_be_int: bool = True
            except ValueError:
                can_data_be_int: bool = False

            if data_type == DataType.INT32 and can_data_be_int:
                self.key_data_map[key] = int(data)
            elif data_type == DataType.UTF8:
                #: Check if data can fit under max length, if not it will be truncated (+1 NULL Terminator)
                if len(data) + 1 > index_table_entry.data_max_length:
                    logger.warning(f'Data too long, truncating to {index_table_entry.data_max_length - 1} bytes...')
                    data = data[0:index_table_entry.data_max_length - 1]

                #: Set Data and add NULL Terminator
                self.key_data_map[key] = data + '\0'

                #: Set Entry data length
                index_table_entry.data_length = len(data) + 1
            elif data_type == DataType.UTF8_SPECIAL:
                #: Check if data can fit under max length, if not it will be truncated
                if len(data) > index_table_entry.data_max_length:
                    logger.warning(f'Data too long, truncating to {index_table_entry.data_max_length} bytes...')
                    data = data[0:index_table_entry.data_max_length]

                #: Set Data
                self.key_data_map[key] = data

                #: Set Entry data length
                index_table_entry.data_length = len(data)
            else:
                logger.error(f'Invalid data type for entry, specified {data_type}')

    def print_key_data_map(self):
        for entry in self.index_table:
            #: Index Table Entry Index
            index: int = self.index_table.index(entry)

            #: SFO Key Data Pair
            key, data = list(self.key_data_map.items())[index]
            logger.info(
                f'Key Data Map Entry #{index} ({entry.data_length}/{entry.data_max_length}): '
                f'{key[:-1]} ({entry.data_type}) -> {data}'
            )

    def write(self, output_file: Optional[str] = None):
        if output_file is None:
            output_file = self.path

            #: Close own file handle because we are about to write to the same file
            self.file_handle.close()

        with open(output_file, 'wb') as f:
            logger.info(f'Writing SFO File...')

            self.header.write(f)

            logger.info(f'Writing SFO Index Table...')

            for i in range(0, self.header.entry_count):
                logger.info(f'Writing SFO Index Table Entry #{i}')
                self.index_table[i].write(f)

            logger.info(f'SFO Index Table Written!')

            logger.info(f'Writing Key -> Data Pair Map...')
            for entry in self.index_table:
                #: Index Table Entry Index
                index: int = self.index_table.index(entry)

                #: SFO Key Data Pair
                key, data = list(self.key_data_map.items())[index]

                #: Seek to entry key offset
                f.seek(self.header.key_table_offset + entry.key_offset)

                #: Write Key
                write_string_null_terminated(f, key, encoding='UTF-8')

                #: Seek to entry data offset
                f.seek(self.header.data_table_offset + entry.data_offset)

                if entry.data_type == DataType.INT32:
                    write_i32(f, data, endianess=Endianess.LITTLE_ENDIAN)
                elif entry.data_type == DataType.UTF8:
                    write_string_null_terminated(f, data, encoding='UTF-8')
                elif entry.data_type == DataType.UTF8_SPECIAL:
                    f.write(data.encode(encoding='UTF-8'))

                #: Write the rest of the unused space
                f.write(bytes(entry.data_max_length - entry.data_length))

            logger.info(f'Key -> Data Pair Map Written!')

            logger.info(f'SFO File Written!')

    def __del__(self):
        logger.info('Cleaning up...')
        if not self.file_handle.closed:
            self.file_handle.close()
