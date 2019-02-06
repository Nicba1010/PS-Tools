from binascii import hexlify
from datetime import datetime
from operator import xor

from aenum import IntFlag, MultiValueEnum

from format._fix_incomplete_iso9660 import InvalidISOException
from format._fix_incomplete_iso9660 import unpack_both_endian_u16, unpack_iso_volume_datetime, unpack_str_a
from utils.utils import unpack_u16, unpack_u8


# TODO: Replace with custom class
class PermissionFlags(IntFlag):
    USER_CANT_READ_FILE = 1
    ALWAYS_TRUE_1 = 2
    USER_CANT_EXECUTE_FILE = 4
    ALWAYS_TRUE_2 = 8
    OWNER_CANT_READ_FILE = 16
    ALWAYS_TRUE_3 = 32
    OWNER_CANT_EXECUTE_FILE = 64
    ALWAYS_TRUE_4 = 128
    ONLY_OWNER_IN_GROUP_CAN_READ_FILE = 256
    ALWAYS_TRUE_5 = 512
    ONLY_OWNER_IN_GROUP_CAN_EXECUTE_FILE = 1024
    ALWAYS_TRUE_6 = 2048
    ONLY_GROUP_USERS_MAY_READ_FILE = 4096
    ALWAYS_TRUE_7 = 8192
    ONLY_GROUP_USERS_MAY_EXECUTE_FILE = 16384
    ALWAYS_TRUE_8 = 32768


class RecordFormat(MultiValueEnum):
    NOT_SPECIFIED = 0
    FIXED_LENGTH_RECORD_SEQUENCE = 1
    VARIABLE_LENGTH_RECORD_SEQUENCE = 2  # RCW recorded according to 7.2.1
    VARIABLE_LENGTH_RECORD_SEQUENCE_2 = 3  # RCW recorded according to 7.2.2
    RESERVED = range(4, 128)
    SYSTEM_USE = range(128, 256)


class RecordAttribute(MultiValueEnum):
    """
    This field contains an 8-bit number specifying certain processing
    of the records in a file when displayed on a character-imaging device.
    """
    BEGIN_LINE_FEED_END_CARRIAGE_RETURN = 0
    ISO_1539 = 1
    EMBEDDED_CONTROL_INFO = 2
    RESERVED = range(3, 256)


class ExtendedAttributeRecord(object):
    def __init__(self, data: bytes):
        #: Owner Identification (if 0 no owner identification specified)
        self.owner_id: int = unpack_both_endian_u16(data[0:4])

        #: Group Identification (if 0 no group identification specified)
        self.group_id: int = unpack_both_endian_u16(data[4:8])

        if xor(self.owner_id == 0, self.group_id == 0):
            raise InvalidISOException(
                f"If either group id, or owner id is zero, both have to be zero. "
                f"In this case owner={self.owner_id}, group={self.group_id}."
            )

        permissions: int = unpack_u16(data[8:10])

        #: Permissions
        self.permission_flags: PermissionFlags = PermissionFlags(permissions)

        #: File Creation Date and Time
        self.file_creation_datetime: datetime = unpack_iso_volume_datetime(data[10:27])

        #: File Modification Date and Time
        self.file_modification_datetime: datetime = unpack_iso_volume_datetime(data[27:44])

        #: File Expiration Date and Time
        self.file_expiration_datetime: datetime = unpack_iso_volume_datetime(data[44:61])

        #: File Effective Date and Time
        self.file_effective_datetime: datetime = unpack_iso_volume_datetime(data[61:78])

        #: Record Format
        self.record_format: RecordFormat = RecordFormat(unpack_u8(data[78:79]))

        #: Record Attributes
        self.record_attributes: RecordAttribute = RecordAttribute(unpack_u8(data[79:80]))

        #: Record Length
        self.record_length: int = unpack_both_endian_u16(data[80:84])

        if self.record_format == RecordFormat.NOT_SPECIFIED and self.record_length != 0:
            raise InvalidISOException(
                f"If record format is 0, record length has to be 0 too. Record length: {self.record_length}"
            )

        #: System Identifier
        self.system_identifier: str = unpack_str_a(data[84:116])

        #: System Used
        self.system_used: bytes = data[116:180]

        #: Extended Attribute Record Version (Always 0x01)
        self.extended_attribute_record_version: int = unpack_u8(data[180:181])
        if self.extended_attribute_record_version != 0x01:
            raise InvalidISOException(
                f"Extended Attribute Record Version is {self.extended_attribute_record_version} instead of 0x01."
            )

        #: Length of Escape Sequences
        self.escape_sequence_length: int = unpack_u8(data[181:182])

        #: Reserved for Future Standardization
        self.reserved: bytes = data[182:246]
        if self.reserved != bytes([0x00] * 64):
            raise InvalidISOException(
                f"Reserved bytes should be all 0x00, instead they are: {hexlify(self.reserved)}"
            )

        #: Length of Application Use
        self.application_use_length: int = unpack_both_endian_u16(data[246:250])

        #: Application Use
        self.application_use: bytes = data[250:250 + self.application_use_length]

        #: Escape Sequences
        self.escape_sequences: bytes = \
            data[250 + self.application_use_length: 250 + self.application_use_length + self.escape_sequence_length]
