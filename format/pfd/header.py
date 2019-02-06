from binascii import hexlify
from typing import IO

from cryptography.hazmat.primitives.ciphers import Cipher, CipherContext

from base.header import MagicFileHeader
from utils.keys import KEYGEN_KEY
from utils.utils import read_u64, Endianess
from .constants import create_syscon_aes_cbc_cipher, hmac_sha256
from .errors import InvalidPFDVersionException

GAME_ID_SIZE = 0x09


class PFDHeader(MagicFileHeader):
    def __init__(self, f: IO):
        super().__init__(f)

        #: File format version
        self.version: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Version: {self.version}')

        #: If version isn't 3 or 4 raise an exception
        if self.version not in (0x03, 0x04):
            raise InvalidPFDVersionException

        #: Header Table IV
        self.header_table_iv: bytes = f.read(16)
        self.logger.info(f'Header Table IV: {hexlify(self.header_table_iv)}')

        #: Header Table Cipher
        self.header_table_cipher: Cipher = create_syscon_aes_cbc_cipher(self.header_table_iv)

        #: Header Table Decryptor
        self.header_table_decryptor: CipherContext = self.header_table_cipher.decryptor()

        #: Header Table Encrypted
        self.header_table_encrypted: bytes = f.read(64)
        self.logger.info(f'Header Table Encrypted: {hexlify(self.header_table_encrypted)}')

        #: Header Table Decrypted
        self.header_data_decrypted: bytearray = bytearray()
        self.header_data_decrypted += self.header_table_decryptor.update(self.header_table_encrypted)
        self.header_data_decrypted += self.header_table_decryptor.finalize()
        self.logger.info(f'Header Table Decrypted: {hexlify(self.header_data_decrypted)}')

        #: Y Table HMAC
        self.y_table_hmac: bytes = bytes(self.header_data_decrypted[0:20])
        self.logger.info(f'Y Table HMAC: {hexlify(self.header_data_decrypted)}')

        #: X Table & Entry Table HMAC
        self.x_table_entry_table_hmac: bytes = bytes(self.header_data_decrypted[20:40])
        self.logger.info(f'X Table & Entry Table HMAC Table HMAC: {hexlify(self.x_table_entry_table_hmac)}')

        #: File HMAC Key
        self.file_hmac_key: bytes = bytes(self.header_data_decrypted[40:60])
        self.logger.info(f'File HMAC Key: {hexlify(self.file_hmac_key)}')

        #: Padding
        self.padding: bytes = bytes(self.header_data_decrypted[60:64])
        self.logger.info(f'Padding: {hexlify(self.padding)}')

        if self.version == 3:
            self.real_key: bytes = self.file_hmac_key
        elif self.version == 4:
            self.real_key: bytes = hmac_sha256(KEYGEN_KEY, self.file_hmac_key)
        self.logger.info(f'Real Key: {hexlify(self.real_key)}')

        #: XY Tables Reserved Entries
        self.xy_tables_reserved_entry_count: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'XY Tables Reserved Entries: {self.xy_tables_reserved_entry_count}')

        #: Protected Files Table Reserved Entries
        self.protected_files_table_reserved_entry_count: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Protected Files Table Reserved Entries: {self.protected_files_table_reserved_entry_count}')

        #: Protected Files Table Used Entries
        self.protected_files_table_used_entry_count: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Protected Files Table Used Entries: {self.protected_files_table_used_entry_count}')

    @property
    def magic(self) -> bytes:
        return b'\0\0\0\0PFDB'
