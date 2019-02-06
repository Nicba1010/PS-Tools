import logging
from binascii import hexlify
from io import BytesIO
from typing import List

# from ..constants import create_syscon_aes_cbc_cipher
from ps.utils import Endianess, read_u64

logger = logging.getLogger('PFD Protected Files Table Entry')


class ProtectedFilesTableEntry(object):
    empty_value = bytes([0x00] * 272)

    def __init__(self, f: BytesIO):
        #: Virtual Index ID
        self.virtual_index_id: bytes = f.read(8)
        logger.info(f'Key Offset: {hexlify(self.virtual_index_id)}')

        #: File Name
        self.file_name: str = f.read(65).decode('UTF-8').strip('\0').strip()
        logger.info(f'File Name: {self.file_name}')

        #: Padding 0
        self.padding_0: bytes = f.read(7)
        logger.info(f'Padding 0: {hexlify(self.padding_0)}')

        #: Key
        self.key: bytes = f.read(64)
        logger.info(f'Key: {hexlify(self.key)}')

        #: Real File Key
        # self.real_table_key: bytes = create_syscon_aes_cbc_cipher()

        #: File Hashes
        self.file_hashes: List[bytes] = []
        for i in range(4):
            file_hash: bytes = f.read(20)
            logger.info(f'File Hash #{i}: {hexlify(file_hash)}')
            self.file_hashes.append(file_hash)

        #: Padding 1
        self.padding_1: bytes = f.read(40)
        logger.info(f'Padding 1: {hexlify(self.padding_1)}')

        #: File Size
        self.file_size: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        logger.info(f'File Size: {self.file_size}')
