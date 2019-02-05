import ctypes
import hashlib
import os
import struct
from ctypes import cdll
from typing import IO

DEFAULT_LOCAL_IO_BLOCK_SIZE = 8 * 1024 * 1024

ps3_aes_key: bytes = bytes(
    [0x2e, 0x7b, 0x71, 0xd7, 0xc9, 0xc9, 0xa1, 0x4e, 0xa3, 0x22, 0x1f, 0x18, 0x88, 0x28, 0xb8, 0xf8]
)
psp_aes_key: bytes = bytes(
    [0x07, 0xf2, 0xc6, 0x82, 0x90, 0xb5, 0x0d, 0x2c, 0x33, 0x81, 0x8d, 0x70, 0x9b, 0x60, 0xe6, 0x2b]
)

max_int64 = 0xFFFFFFFFFFFFFFFF

xor_lib_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), './xor.lib')
xor_c_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), './xor.c')
# if not os.path.exists(xor_lib_path):
# TODO: Fix
# subprocess.check_output(['gcc', xor_c_path, '-shared', '-std=c99', '-O3'])

if os.name == 'nt':
    xor_lib = cdll.LoadLibrary(xor_lib_path)
    xor_lib.generate_xor_key.argtypes = [ctypes.c_char_p, ctypes.c_longlong, ctypes.c_longlong, ctypes.c_char_p]
    xor_lib.add.argtypes = [ctypes.c_char_p, ctypes.c_longlong, ctypes.c_longlong]
    xor_lib.xor.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_longlong, ctypes.c_longlong]


def human_size(size_: int, format_: str = '3.2'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(size_) < 1024.0:
            return f"{size_:{format_}f} {unit}B"
        size_ /= 1024.0
    return f"{size_:.1f} YiB"


def file_md5(filename: str, block_size=4096) -> bytes:
    hasher: hashlib = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            hasher.update(block)
    return hasher.hexdigest()


class Endianess(object):
    LITTLE_ENDIAN: str = '<'
    BIG_ENDIAN: str = '>'


def unpack_string_null_terminated(data: bytes, encoding: str = 'UTF-8') -> str:
    return data[0:data.index(0x00)].decode(encoding)


def read_string_null_terminated(f: IO, encoding: str = 'UTF-8') -> str:
    string_data: bytearray = bytearray()
    while len(string_data) == 0x00 or string_data[len(string_data) - 1] != 0x00:
        string_data += f.read(1)
    return string_data.decode(encoding)


def write_string_null_terminated(f: IO, data: str, encoding: str = 'UTF-8') -> None:
    if not data[-1] == '\0':
        data += '\0'
    f.write(data.encode(encoding))


def unpack_u8(data: bytes, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return struct.unpack(endianess + 'B', data)[0]


def read_u8(f: IO, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return unpack_u8(f.read(1), endianess=endianess)


def pack_u8(data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> bytes:
    return struct.pack(endianess + 'B', data)


def write_u8(f: IO, data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> None:
    f.write(pack_u8(data, endianess=endianess))


def unpack_u16(data: bytes, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return struct.unpack(endianess + 'H', data)[0]


def read_u16(f: IO, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return unpack_u16(f.read(2), endianess=endianess)


def pack_u16(data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> bytes:
    return struct.pack(endianess + 'H', data)


def write_u16(f: IO, data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> None:
    f.write(pack_u16(data, endianess=endianess))


def unpack_u32(data: bytes, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return struct.unpack(endianess + 'I', data)[0]


def read_u32(f: IO, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return unpack_u32(f.read(4), endianess=endianess)


def pack_u32(data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> bytes:
    return struct.pack(endianess + 'I', data)


def write_u32(f: IO, data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> None:
    f.write(pack_u32(data, endianess=endianess))


def unpack_u64(data: bytes, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return struct.unpack(endianess + 'Q', data)[0]


def read_u64(f: IO, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return unpack_u64(f.read(8), endianess=endianess)


def pack_u64(data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> bytes:
    return struct.pack(endianess + 'Q', data)


def write_u64(f: IO, data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> None:
    f.write(pack_u64(data, endianess=endianess))


def unpack_i8(data: bytes, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return struct.unpack(endianess + 'b', data)[0]


def read_i8(f: IO, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return unpack_i8(f.read(1), endianess=endianess)


def pack_i8(data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> bytes:
    return struct.pack(endianess + 'b', data)


def write_i8(f: IO, data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> None:
    f.write(pack_i8(data, endianess=endianess))


def unpack_i16(data: bytes, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return struct.unpack(endianess + 'h', data)[0]


def read_i16(f: IO, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return unpack_i16(f.read(2), endianess=endianess)


def pack_i16(data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> bytes:
    return struct.pack(endianess + 'h', data)


def write_i16(f: IO, data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> None:
    f.write(pack_i16(data, endianess=endianess))


def unpack_i32(data: bytes, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return struct.unpack(endianess + 'i', data)[0]


def read_i32(f: IO, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return unpack_i32(f.read(4), endianess=endianess)


def pack_i32(data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> bytes:
    return struct.pack(endianess + 'i', data)


def write_i32(f: IO, data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> None:
    f.write(pack_i32(data, endianess=endianess))


def unpack_i64(data: bytes, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return struct.unpack(endianess + 'q', data)[0]


def read_i64(f: IO, endianess: str = Endianess.LITTLE_ENDIAN) -> int:
    return unpack_i64(f.read(8), endianess=endianess)


def pack_i64(data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> bytes:
    return struct.pack(endianess + 'q', data)


def write_i64(f: IO, data: int, endianess: str = Endianess.LITTLE_ENDIAN) -> None:
    f.write(pack_i64(data, endianess=endianess))
