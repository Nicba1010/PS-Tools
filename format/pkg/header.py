from binascii import hexlify
from typing import IO

from base.header import MagicFileHeader
from base.utils import constant_check
from utils.utils import read_u32, read_u64, Endianess
from .key_id import PkgKeyID
from .revision import PkgRevision
from .type import PkgType


class PkgExtHeader(MagicFileHeader):
    def __init__(self, f: IO):
        super().__init__(f)

        self.unknown_1: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        constant_check(self.logger, 'Unknown 1', self.unknown_1, 1)

        self.header_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Header Size: {self.header_size}')

        self.data_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Data Size: {self.data_size}')

        self.main_and_ext_headers_hmac_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Main and Ext Headers HMAC Offset: {self.main_and_ext_headers_hmac_offset}')

        self.metadata_header_hmac_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Metadata Header HMAC Offset: {self.metadata_header_hmac_offset}')

        self.tail_offset: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Tail Offset: {self.tail_offset}')

        self.padding_1: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        constant_check(self.logger, 'Padding 1', self.padding_1, 0)

        self.pkg_key_id: PkgKeyID = PkgKeyID(read_u32(f, endianess=Endianess.BIG_ENDIAN))
        self.logger.info(f'PKG Key ID: {self.pkg_key_id}')

        self.full_header_hmac_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Full Header HMAC Offset: {self.full_header_hmac_offset}')

        self.padding_2: bytes = f.read(0x14)
        constant_check(self.logger, 'Padding 2', self.padding_2, bytes([0x00] * 0x14))

    @property
    def magic(self) -> bytes:
        return b'\x7fext'


class PkgHeader(MagicFileHeader):
    def __init__(self, f: IO):
        super().__init__(f)

        self.revision: PkgRevision = PkgRevision(f.read(2))
        self.type: PkgType = PkgType(f.read(2))
        self.logger.info(f'PKG Revision: {self.revision}')
        self.logger.info(f'PKG Type: {self.type}')

        self.metadata_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.metadata_count: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.metadata_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Metadata Offset: {self.metadata_offset}')
        self.logger.info(f'Metadata Count: {self.metadata_count}')
        self.logger.info(f'Metadata Size: {self.metadata_size}')

        self.item_count: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Item Count: {self.item_count}')

        self.total_size: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.data_offset: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.data_size: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Total Size: {self.total_size}')
        self.logger.info(f'Data Offset: {self.data_offset}')
        self.logger.info(f'Data Size: {self.data_size}')

        self.content_id: str = f.read(0x24).decode('utf-8')
        self.logger.info(f'Content ID: {self.content_id}')

        self.padding: bytes = f.read(0x0C)

        self.digest: bytes = f.read(0x10)
        self.pkg_data_riv: bytes = f.read(0x10)
        self.header_cmac_hash: bytes = f.read(0x10)
        self.header_npdrm_signature: bytes = f.read(0x28)
        self.header_sha1_hash: bytes = f.read(0x08)
        self.logger.info(f'Digest: {hexlify(self.digest)}')
        self.logger.info(f'PKG Data Riv: {self.pkg_data_riv}')
        self.logger.info(f'Header CMAC Hash: {hexlify(self.header_cmac_hash)}')
        self.logger.info(f'Header NPDRM Signature: {hexlify(self.header_npdrm_signature)}')
        self.logger.info(f'Header SHA1 Hash: {hexlify(self.header_sha1_hash)}')

        if self.type == PkgType.PSP_PSVITA:
            self.ext_header: PkgExtHeader = PkgExtHeader(f)

    @property
    def magic(self) -> bytes:
        return b'\x7fPKG'
