from datetime import datetime

from aenum import IntFlag

from format._fix_incomplete_iso9660 import InvalidISOException
from format._fix_incomplete_iso9660 import unpack_both_endian_u32, unpack_both_endian_u16, unpack_str_a, \
    unpack_directory_record_datetime
from utils.utils import unpack_u8


class FileFlags(IntFlag):
    EXISTENCE = 1  # If TRUE, user doesn't need to know about file
    DIRECTORY = 2  # If TRUE, record identifies a directory
    ASSOCIATED_FILE = 4  # If TRUE, file is an Associated File
    RECORD = 8  # If TRUE, structure in file has a format specified in the Extended Attribute Record
    PROTECTION = 16  # If TRUE, owner specified for file also one+ of the even bits is set to 1 in the EAR
    RESERVED_1 = 32
    RESERVED_2 = 64
    MULTI_EXTENT = 128  # If TRUE, not the final Directory Record for the file


class DirectoryRecord(object):
    def __init__(self, data: bytes):
        #: Directory Record Length
        self.length: int = unpack_u8(data[0:1])

        #: Extended Attribute Record Length
        self.extended_attribute_record_length: int = unpack_u8(data[1:2])

        #: Location of LBA LSB&MSB
        self.lba_location: int = unpack_both_endian_u32(data[2:10])

        #: Data Length LSB&MSB
        self.data_length: int = unpack_both_endian_u32(data[10:18])

        #: Recording Date and Time
        self.recording_datetime: datetime = unpack_directory_record_datetime(data[18:25])

        #: File Flags
        self.file_flags: FileFlags = FileFlags(data[25])

        #: File Unit Size
        self.file_unit_size: int = unpack_u8(data[26:27])

        #: Interleave gap size for files recorded in interleaved mode, 0x00 otherwise
        self.interleave_gap: int = unpack_u8(data[27:28])

        #: Volume Sequence Number (Number of Disk this is recorded on) LSB & MSB
        self.volume_sequence_number: int = unpack_both_endian_u16(data[28:32])

        #: File Identifier Length (File Name)
        self.file_identifier_length: int = unpack_u8(data[32:33])

        file_identifier_end_offset: int = 33 + self.file_identifier_length

        #: File Identifier
        self.file_identifier: str = unpack_str_a(data[33:33 + self.file_identifier_length])

        #: Padding (None if file identifier length even, the field does not exist in that case)
        self.padding: int
        if self.file_identifier_length % 2 == 0 or self.file_identifier == b'\x00'.decode('ASCII'):
            self.padding = None
        else:
            self.padding = data[file_identifier_end_offset]
        if self.padding is not None and self.padding != 0x00:
            raise InvalidISOException("Directory Record Padding is {hex(self.padding)} instead of 0x00 or None")

        # TODO: Implement Extensions! Also System Use Field!
