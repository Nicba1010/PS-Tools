import logging
import os
from binascii import hexlify
from io import BytesIO
from typing import List, Optional

from .errors import EmptyPFDException, InvalidFieldException
from .header import PFDHeader
from .protected_files_table import ProtectedFilesTableEntry

logger = logging.getLogger('PFD')


class PFD(object):
    eof_padding = bytes([0x00] * 44)

    def __init__(self, path: str):
        #: File Path
        self.path: str = path
        logger.info(f'Parsing file: {self.path}')

        if os.stat(self.path).st_size == 0:
            logger.error('Error, file is empty')
            raise EmptyPFDException()

        #: File Handle
        self.file_handle: BytesIO = open(self.path, 'rb')

        #: File Header
        self.header: PFDHeader = PFDHeader(self.file_handle)

        #: X Table
        self.x_table: List[bytes] = []
        logger.info(f'Reading X Table...')
        for i in range(self.header.xy_tables_reserved_entry_count):
            x_table_entry: bytes = self.file_handle.read(8)
            logger.debug(f'X Table Entry #{i}: {hexlify(x_table_entry)}')
            self.x_table.append(x_table_entry)

        #: Protected Files Table
        self.protected_files_table: List[Optional[ProtectedFilesTableEntry]] = []
        logger.info(f'Reading Protected Files Table...')
        for i in range(self.header.protected_files_table_reserved_entry_count):
            if i < self.header.protected_files_table_used_entry_count:
                logger.info(f'Protected File Entry #{i}:')
                protected_file_entry: Optional[ProtectedFilesTableEntry] = ProtectedFilesTableEntry(self.file_handle)
                self.protected_files_table.append(protected_file_entry)
            else:
                #: Empty Protected File Entry (0x00*272)
                empty_entry_data: bytes = self.file_handle.read(272)
                if empty_entry_data != ProtectedFilesTableEntry.empty_value:
                    raise InvalidFieldException(
                        f'Protected File Entry (Empty) #{i}', empty_entry_data, ProtectedFilesTableEntry.empty_value
                    )
                else:
                    logger.debug(f'Protected File Entry #{i}: None')

        #: Y Table
        self.y_table: List[bytes] = []
        logger.info(f'Reading Y Table...')
        for i in range(self.header.xy_tables_reserved_entry_count):
            #: Y Table Entry (20 byte SHA1-HMAC)
            y_table_entry: bytes = self.file_handle.read(20)
            logger.debug(f'Y Table Entry #{i}: {hexlify(y_table_entry)}')

            self.y_table.append(y_table_entry)

        #: Padding (0x00 * 44)
        self.padding: bytes = self.file_handle.read(44)
        if self.padding != PFD.eof_padding:
            raise InvalidFieldException(f'EOF Padding', self.padding, PFD.eof_padding)
        else:
            logger.info(f'Padding: {hexlify(self.padding)}')

    def __del__(self):
        logger.debug('Cleaning up...')
        if not self.file_handle.closed:
            self.file_handle.close()
