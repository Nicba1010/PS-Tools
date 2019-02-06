import zlib
from typing import IO, Generator

from utils.utils import Endianess, unpack_u16


def psarc_zlib_multi_stream_unpack(f: IO, unpacked_size: int, block_size: int) -> Generator[bytes, None, None]:
    # TODO: Optimize to C in the future
    total_data_unpacked: int = 0
    data: bytes = f.read(block_size)
    while len(data) > 0 and total_data_unpacked < unpacked_size:
        zlib_header: int = unpack_u16(data[:2], endianess=Endianess.BIG_ENDIAN)

        is_file_zlib_compressed: bool = data[0] == 0x78 and zlib_header % 31 == 0

        if is_file_zlib_compressed:
            dec = zlib.decompressobj(zlib.MAX_WBITS)
            chunk_data: bytes = dec.decompress(data)
            data = dec.unused_data
        else:
            chunk_data: bytes = data[:min(block_size, unpacked_size - total_data_unpacked)]

        total_data_unpacked += len(chunk_data)

        if chunk_data:
            yield chunk_data
        else:
            return

        data += (f.read(block_size) if len(data) < block_size else bytes())
