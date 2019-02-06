from format._fix_incomplete_iso9660.errors import InvalidISOException
from format._fix_incomplete_iso9660.utils import unpack_str_d
from utils.utils import unpack_u8, unpack_u32, unpack_u16, Endianess


class PathTableRecord(object):
    def __init__(self, data: bytes):
        #: Directory Identifier Length
        self.directory_identifier_length: int = unpack_u8(data[0:1])

        #: Extended Attribute Record Length
        self.extended_attribute_record_length: int = unpack_u8(data[1:2])

        #: Location of Extent
        self.extent_location: int = unpack_u32(data[2:6], endianess=Endianess.LITTLE_ENDIAN)

        #: Parent Directory Number (specified record number of parent directory entry in path table)
        self.parent_directory_number: int = unpack_u16(data[6:8], endianess=Endianess.LITTLE_ENDIAN)

        directory_identifier_end_offset: int = 8 + self.directory_identifier_length

        #: Directory Identifier
        self.directory_identifier: str = unpack_str_d(data[8:directory_identifier_end_offset])

        #: Padding (None if file identifier length even, the field does not exist in that case)
        self.padding: int

        #: Total Path Table Record Binary Size
        self.size: int
        if self.directory_identifier_length % 2 == 0:
            self.padding = None
            self.size = directory_identifier_end_offset
        else:
            self.padding = data[directory_identifier_end_offset]
            self.size = directory_identifier_end_offset + 1
        if self.padding is not None and self.padding != 0x00:
            raise InvalidISOException("Directory Record Padding is {hex(self.padding)} instead of 0x00 or None")

        #: Path Table Record Size

    def __repr__(self):
        return f"<PathTableRecord id='{self.directory_identifier}' parent='{self.parent_directory_number}')>"
