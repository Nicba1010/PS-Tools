import ctypes
import os
import struct
import subprocess

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
if not os.path.exists(xor_lib_path):
    # TODO: Fix
    subprocess.check_output(['gcc', xor_c_path, '-shared', '-std=c99', '-O3'])

xor_lib = cdll.LoadLibrary(xor_lib_path)
xor_lib.generate_xor_key.argtypes = [ctypes.c_char_p, ctypes.c_longlong, ctypes.c_longlong, ctypes.c_char_p]
xor_lib.add.argtypes = [ctypes.c_char_p, ctypes.c_longlong, ctypes.c_longlong]
xor_lib.xor.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_longlong, ctypes.c_longlong]


def read_u16(f: IO, endianess: str = '>') -> int:
    return struct.unpack(endianess + 'H', f.read(2))[0]


def read_u32(f: IO, endianess: str = '>') -> int:
    return struct.unpack(endianess + 'I', f.read(4))[0]


def read_u64(f: IO, endianess: str = '>') -> int:
    return struct.unpack(endianess + 'Q', f.read(8))[0]
