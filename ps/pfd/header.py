import logging
from binascii import hexlify
from io import BytesIO

from cryptography.hazmat.primitives.ciphers import Cipher, CipherContext

from ps.keys import KEYGEN_KEY
from ps.utils import read_u64, Endianess
from .constants import magic, get_header_table_cipher, hmac_sha256
from .errors import InvalidPFDException, InvalidPFDVersionException

GAME_ID_SIZE = 0x09

logger = logging.getLogger('PFD Header')


class PFDHeader(object):
    def __init__(self, f: BytesIO):
        #: Magic
        self.magic: bytes = f.read(8)
        logger.info(f'Magic: {self.magic}')

        if self.magic != magic:
            logger.error('Error, invalid magic')
            raise InvalidPFDException
        else:
            logger.info('Magic Verified')

        #: File format version
        self.version: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        logger.info(f'Version: {self.version}')

        #: If version isn't 3 or 4 raise an exception
        if self.version not in (0x03, 0x04):
            raise InvalidPFDVersionException

        #: Header Table IV
        self.header_table_iv: bytes = f.read(16)
        logger.info(f'Header Table IV: {hexlify(self.header_table_iv)}')

        #: Header Table Cipher
        self.header_table_cipher: Cipher = get_header_table_cipher(self.header_table_iv)

        #: Header Table Decryptor
        self.header_table_decryptor: CipherContext = self.header_table_cipher.decryptor()

        #: Header Table Encrypted
        self.header_table_encrypted: bytes = f.read(64)
        logger.info(f'Header Table Encrypted: {hexlify(self.header_table_encrypted)}')

        #: Header Table Decrypted
        self.header_data_decrypted: bytearray = bytearray()
        self.header_data_decrypted += self.header_table_decryptor.update(self.header_table_encrypted)
        self.header_data_decrypted += self.header_table_decryptor.finalize()
        logger.info(f'Header Table Decrypted: {hexlify(self.header_data_decrypted)}')

        #: Y Table HMAC
        self.y_table_hmac: bytes = bytes(self.header_data_decrypted[0:20])
        logger.info(f'Y Table HMAC: {hexlify(self.header_data_decrypted)}')

        #: X Table & Entry Table HMAC
        self.x_table_entry_table_hmac: bytes = bytes(self.header_data_decrypted[20:40])
        logger.info(f'X Table & Entry Table HMAC Table HMAC: {hexlify(self.x_table_entry_table_hmac)}')

        #: File HMAC Key
        self.file_hmac_key: bytes = bytes(self.header_data_decrypted[40:60])
        logger.info(f'File HMAC Key: {hexlify(self.file_hmac_key)}')

        #: Padding
        self.padding: bytes = bytes(self.header_data_decrypted[60:64])
        logger.info(f'Padding: {hexlify(self.padding)}')

        if self.version == 3:
            self.real_key: bytes = self.file_hmac_key
        elif self.version == 4:
            self.real_key: bytes = hmac_sha256(KEYGEN_KEY, self.file_hmac_key)
        logger.info(f'Real Key: {hexlify(self.real_key)}')

        #: XY Tables Reserved Entries
        self.xy_tables_reserved_entry_count: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        logger.info(f'XY Tables Reserved Entries: {self.xy_tables_reserved_entry_count}')

        #: Protected Files Table Reserved Entries
        self.protected_files_table_reserved_entry_count: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        logger.info(f'Protected Files Table Reserved Entries: {self.protected_files_table_reserved_entry_count}')

        #: Protected Files Table Used Entries
        self.protected_files_table_used_entry_count: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        logger.info(f'Protected Files Table Used Entries: {self.protected_files_table_used_entry_count}')
