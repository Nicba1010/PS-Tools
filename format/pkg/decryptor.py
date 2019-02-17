from binascii import hexlify
from typing import IO, AnyStr, List, Optional, Dict

from cryptography.hazmat.primitives.ciphers import CipherContext, Cipher, algorithms, modes

from base import LoggingClass
from utils.utils import xor_lib, backend
from .header import PkgHeader
from .revision import PkgRevision
from .type import PkgType


class PkgInternalIO(IO, LoggingClass):
    SEEK_DATA_OFFSET: int = 4

    def __init__(self, f: IO, header: PkgHeader, encryption_key: Optional[bytes]):
        super().__init__()
        self.header: PkgHeader = header
        self.f: IO = f

        self.encryption_key: Optional[bytes] = encryption_key
        self.cipher: Optional[Cipher] = None
        self.encryptor: Optional[CipherContext] = None

        self.alternate_ciphers: Dict[bytes, Cipher] = {}
        self.alternate_encryptors: Dict[bytes, CipherContext] = {}

        if self.header.revision == PkgRevision.RETAIL:
            if encryption_key is None:
                raise ValueError('Encryptor key was not supplied even though the PKG is a Retail PKG.')
            self.cipher = Cipher(algorithms.AES(self.encryption_key), modes.ECB(), backend=backend)
            self.encryptor = self.cipher.encryptor()
            self.logger.info('Encryptor initialized...')

    def __enter__(self) -> 'PkgInternalIO':
        return self

    def __exit__(self, ext_type, ext_val, ext_trace) -> None:
        pass

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == PkgInternalIO.SEEK_DATA_OFFSET:
            return self.f.seek(offset + self.header.data_offset)
        else:
            return self.f.seek(offset, whence)

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.f.tell()

    def generate_xor(self, starting_offset: int, size: int, encryptor: Optional[CipherContext]):
        #: Because of how the AES-128 encryption, we need to expand the xor key size to the next multiple of 16
        xor_key_size = xor_lib.next_multiple_of_16(size)
        #: Allocate memory for the key
        xor_key: bytes = bytes(xor_key_size)

        # 16-byte blocks since header specified DATA_OFFSET
        block_offset: int = (starting_offset - self.header.data_offset) // 16
        # IMPORTANT: This increments pkg_data_riv by 1
        if self.header.revision == PkgRevision.RETAIL:
            #: Generate the retail xor key
            xor_lib.generate_xor_key(self.header.pkg_data_riv, xor_key_size, block_offset, xor_key)
            #: Finalize xor key
            return encryptor.update(bytes(xor_key))
        else:
            #: Generate the debug xor key (no encryption needed)
            return bytes(xor_lib.generate_debug_xor_key(self.header.digest, xor_key_size, block_offset, xor_key))

    def read(self, n: int = -1, alternate_encryption_key: Optional[bytes] = None) -> AnyStr:
        #: Copy offset to a variable so that we don't call tell() twice
        offset: int = self.f.tell()
        #: Get the xor offset (absolute position in data block aligned to 16)
        xor_offset: int = (offset - self.header.data_offset) % 16

        #: Check for alternate encryption key
        if alternate_encryption_key is not self.encryption_key and alternate_encryption_key is not None:
            #: Check if cipher context for said key is initialized
            if alternate_encryption_key not in self.alternate_encryptors.keys():
                #: Initialize cipher context
                self.init_alternate_cipher(alternate_encryption_key)
            #: Generate xor key using the alternate encryption key
            xor_key: bytes = self.generate_xor(offset, n, self.alternate_encryptors[alternate_encryption_key])
        else:
            #: Generate xor key using the default encryption key
            xor_key: bytes = self.generate_xor(offset, n, self.encryptor)

        buffer: bytes = self.f.read(n)
        xor_lib.xor(buffer, xor_key, len(buffer), xor_offset)

        return buffer

    def readable(self) -> bool:
        return True

    def writable(self) -> bool:
        return False

    def write(self, s: AnyStr) -> int:
        pass

    def writelines(self, lines: List[AnyStr]) -> None:
        pass

    def init_alternate_cipher(self, alternate_encryption_key: bytes) -> None:
        """
        Initializes the alternate cipher context using the specified encryption key.
        :param alternate_encryption_key: encryption key
        :return: Nothing
        """
        #: Initialize AES ECB cipher with alternate_encryption_key
        cipher: Cipher = Cipher(algorithms.AES(alternate_encryption_key), modes.ECB(), backend=backend)
        #: Initialize AES ECB cipher context
        encryptor: CipherContext = cipher.encryptor()
        #: Add cipher to alternate_ciphers dict
        self.alternate_ciphers[alternate_encryption_key] = cipher
        #: Add encryptor to alternate_encryptors dict
        self.alternate_encryptors[alternate_encryption_key] = encryptor
        self.logger.debug(f'Alternate Cipher initialized for key {hexlify(alternate_encryption_key).decode("ASCII")}')
