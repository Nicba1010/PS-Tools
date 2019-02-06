from typing import IO, AnyStr, List

from ps.utils import xor_lib
from .header import PkgHeader


# noinspection PyAbstractClass
class DecryptorIO(IO):
    SEEK_DATA_OFFSET: int = 4

    def __init__(self, header: PkgHeader, f: IO):
        self.encryptor = header.encryptor
        self.header: PkgHeader = header
        self.f: IO = f

    def __enter__(self) -> 'DecryptorIO':
        return self

    def __exit__(self, ext_type, ext_val, ext_trace) -> None:
        pass

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == DecryptorIO.SEEK_DATA_OFFSET:
            return self.f.seek(offset + self.header.data_offset)
        else:
            return self.f.seek(offset, whence)

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.f.tell()

    def generate_xor(self, starting_offset: int, size: int):
        xor_key_size = xor_lib.next_multiple_of_16(size)
        xor_key: bytes = bytes(xor_key_size)

        # 16-byte blocks since header specified DATA_OFFSET
        block_offset: int = (starting_offset - self.header.data_offset) // 16
        # IMPORTANT: This increments pkg_data_riv by 1
        xor_lib.generate_xor_key(self.header.pkg_data_riv, xor_key_size, block_offset, xor_key)
        return self.encryptor.update(bytes(xor_key))

    def readable(self) -> bool:
        return True

    def read(self, n: int = -1) -> AnyStr:
        offset: int = self.f.tell()
        xor_offset: int = (offset - self.header.data_offset) % 16
        xor_key: bytes = self.generate_xor(offset, n)
        buffer: bytes = self.f.read(n)
        xor_lib.xor(buffer, xor_key, len(buffer), xor_offset)
        return buffer

    def writable(self) -> bool:
        return False

    def write(self, s: AnyStr) -> int:
        pass

    def writelines(self, lines: List[AnyStr]) -> None:
        pass
