import re
from datetime import datetime
from typing import Optional

from format._fix_incomplete_iso9660 import InvalidValueLSBMSBEncodeException, InvalidStringEncodeException
from utils.errors import InvalidISODateException
from utils.utils import unpack_u16, unpack_u32, unpack_u64, unpack_i8, unpack_i16, unpack_i32, unpack_i64, \
    Endianess, unpack_u8

str_a_regex: re = re.compile('[ A-Za-z0-9_!"%&\'()*+,\-./:;<=>?]*')
str_d_regex: re = re.compile('[ A-Z0-9_]*')


def unpack_str_a(data: bytes) -> str:
    decoded: str = data.decode('ASCII')
    if not str_a_regex.match(decoded):
        raise InvalidStringEncodeException(mode='A', string=decoded)
    else:
        return decoded


def unpack_str_d(data: bytes) -> str:
    decoded: str = data.decode('ASCII')
    if not str_d_regex.match(decoded):
        raise InvalidStringEncodeException(mode='D', string=decoded)
    else:
        return decoded


def unpack_both_endian_u16(data: bytes) -> int:
    #: Little Endian Value
    le_val: int = unpack_u16(data[0:2], endianess=Endianess.LITTLE_ENDIAN)
    #: Big Endian Value
    be_val: int = unpack_u16(data[2:4], endianess=Endianess.BIG_ENDIAN)

    if le_val != be_val:
        raise InvalidValueLSBMSBEncodeException(le_val, be_val)
    else:
        return le_val


def unpack_both_endian_u32(data: bytes) -> int:
    #: Little Endian Value
    le_val: int = unpack_u32(data[0:4], endianess=Endianess.LITTLE_ENDIAN)
    #: Big Endian Value
    be_val: int = unpack_u32(data[4:8], endianess=Endianess.BIG_ENDIAN)

    if le_val != be_val:
        raise InvalidValueLSBMSBEncodeException(le_val, be_val)
    else:
        return le_val


def unpack_both_endian_u64(data: bytes) -> int:
    #: Little Endian Value
    le_val: int = unpack_u64(data[0:8], endianess=Endianess.LITTLE_ENDIAN)
    #: Big Endian Value
    be_val: int = unpack_u64(data[8:16], endianess=Endianess.BIG_ENDIAN)

    if le_val != be_val:
        raise InvalidValueLSBMSBEncodeException(le_val, be_val)
    else:
        return le_val


def unpack_both_endian_i16(data: bytes) -> int:
    #: Little Endian Value
    le_val: int = unpack_i16(data[0:2], endianess=Endianess.LITTLE_ENDIAN)
    #: Big Endian Value
    be_val: int = unpack_i16(data[2:4], endianess=Endianess.BIG_ENDIAN)

    if le_val != be_val:
        raise InvalidValueLSBMSBEncodeException(le_val, be_val)
    else:
        return le_val


def unpack_both_endian_i32(data: bytes) -> int:
    #: Little Endian Value
    le_val: int = unpack_i32(data[0:4], endianess=Endianess.LITTLE_ENDIAN)
    #: Big Endian Value
    be_val: int = unpack_i32(data[4:8], endianess=Endianess.BIG_ENDIAN)

    if le_val != be_val:
        raise InvalidValueLSBMSBEncodeException(le_val, be_val)
    else:
        return le_val


def unpack_both_endian_i64(data: bytes) -> int:
    #: Little Endian Value
    le_val: int = unpack_i64(data[0:8], endianess=Endianess.LITTLE_ENDIAN)
    #: Big Endian Value
    be_val: int = unpack_i64(data[8:16], endianess=Endianess.BIG_ENDIAN)

    if le_val != be_val:
        raise InvalidValueLSBMSBEncodeException(le_val, be_val)
    else:
        return le_val


def unpack_directory_record_datetime(data: bytes) -> Optional[datetime]:
    if data == bytes([0x00] * 7):
        return None

    year: int = unpack_u8(data[0:1]) + 1900
    month: int = unpack_u8(data[1:2])
    day: int = unpack_u8(data[2:3])
    hour: int = unpack_u8(data[3:4])
    minute: int = unpack_u8(data[4:5])
    second: int = unpack_u8(data[5:6])
    timezone: int = unpack_u8(data[6:7])

    if not 1 <= month <= 12:
        raise InvalidISODateException(f"Month out of range (1 <= month <= 12): {month}")
    if not 1 <= day <= 31:
        raise InvalidISODateException(f"Day out of range (1 <= day <= 31): {day}")
    if not 0 <= hour <= 23:
        raise InvalidISODateException(f"Hour out of range (1 <= hour <= 23): {hour}")
    if not 0 <= minute <= 59:
        raise InvalidISODateException(f"Minute out of range (1 <= minute <= 59): {minute}")
    if not 0 <= second <= 59:
        raise InvalidISODateException(f"Second out of range (1 <= second <= 59): {second}")
    if not -12 <= timezone <= 13:
        raise InvalidISODateException(f"Timezone out of range (-12 <= millisecond <= -13): {timezone}")
    # TODO: Add timezone to result
    return datetime(year, month, day, hour, minute, second)


def unpack_iso_volume_datetime(data: bytes) -> Optional[datetime]:
    #: Check if datetime is not specified
    if data == b'0000000000000000\x00':
        return None

    year: int = int(data[0:4].decode('ASCII'))
    month: int = int(data[4:6].decode('ASCII'))
    day: int = int(data[6:8].decode('ASCII'))
    hour: int = int(data[8:10].decode('ASCII'))
    minute: int = int(data[10:12].decode('ASCII'))
    second: int = int(data[12:14].decode('ASCII'))
    millisecond: int = int(data[14:16].decode('ASCII')) * 10
    timezone: int = unpack_i8(data[16:17]) / 4
    if not 1 <= year <= 9999:
        raise InvalidISODateException(f"Year out of range (1 <= year <= 9999): {year}")
    if not 1 <= month <= 12:
        raise InvalidISODateException(f"Month out of range (1 <= month <= 12): {month}")
    if not 1 <= day <= 31:
        raise InvalidISODateException(f"Day out of range (1 <= day <= 31): {day}")
    if not 0 <= hour <= 23:
        raise InvalidISODateException(f"Hour out of range (1 <= hour <= 23): {hour}")
    if not 0 <= minute <= 59:
        raise InvalidISODateException(f"Minute out of range (1 <= minute <= 59): {minute}")
    if not 0 <= second <= 59:
        raise InvalidISODateException(f"Second out of range (1 <= second <= 59): {second}")
    if not 0 <= millisecond <= 990:
        raise InvalidISODateException(f"Millisecond out of range (1 <= millisecond <= 990): {millisecond}")
    if not -12 <= timezone <= 13:
        raise InvalidISODateException(f"Timezone out of range (-12 <= timezone <= -13): {timezone}")
    # TODO: Add timezone to result
    return datetime(year, month, day, hour, minute, second, millisecond * 1000)
