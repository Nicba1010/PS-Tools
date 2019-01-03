from binascii import hexlify
from datetime import datetime
from typing import Optional

from aenum import IntFlag

from ps.iso9660.directory_record import DirectoryRecord
from ps.iso9660.errors import InvalidISOException
from ps.iso9660.utils import unpack_str_a, unpack_str_d, unpack_both_endian_i32, unpack_both_endian_i16, \
    unpack_iso_volume_datetime
from ps.utils import unpack_i32, Endianess
from .base import BaseVolumeDescriptor


class VolumeFlags(IntFlag):
    ISO_2375_COMPLIANT = 1
    UNUSED_1 = 2
    UNUSED_2 = 4
    UNUSED_3 = 8
    UNUSED_4 = 16
    UNUSED_5 = 32
    UNUSED_6 = 64
    UNUSED_7 = 128


class SupplementaryVolumeDescriptor(BaseVolumeDescriptor):
    def __init__(self, data: bytes):
        super().__init__(data)

        #: Volume Flags
        self.volume_flags: VolumeFlags = VolumeFlags(data[7])

        #: The System Identifier
        self.system_identifier: str = unpack_str_a(data[8:40])

        #: The Volume Identifier
        self.volume_identifier: str = unpack_str_d(data[40:72])

        #: Unused Field (8 x 0x00)
        self.unused_2: bytes = data[72:80]
        if self.unused_2 != bytes([0x00] * 8):
            raise InvalidISOException(
                f"Unused field at index 72 should always be 8 x 0x00. Instead it is {hexlify(self.unused_2)}."
            )

        #: Volume Space Size (Number of Logical Blocks) LSB & MSB
        self.volume_space_size: int = unpack_both_endian_i32(data[80:88])

        #: Unused Field (32 x 0x00)
        self.unused_3: bytes = data[88:120]
        if self.unused_3 != bytes([0x00] * 32):
            raise InvalidISOException(
                f"Unused field at index 88 should always be 32 x 0x00. Instead it is{hexlify(self.unused_3)}."
            )

        #: Volume Set Size (Number of Disks) LSB & MSB
        self.volume_set_size: int = unpack_both_endian_i16(data[120:124])

        #: Volume Sequence Number (Number of this Disk) LSB & MSB
        self.volume_sequence_number: int = unpack_both_endian_i16(data[124:128])

        #: Logical Block Size LSB & MSB
        self.logical_block_size: int = unpack_both_endian_i16(data[128:132])

        #: Path Table Size LSB & MSB
        self.path_table_size: int = unpack_both_endian_i32(data[132:140])

        #: Location of Type-L Path Table
        self.l_path_table_location: int = unpack_i32(data[140:144], endianess=Endianess.LITTLE_ENDIAN)

        #: Location of Optional Type-L Path Table
        self.optional_l_path_table_location: int = unpack_i32(data[144:148], endianess=Endianess.LITTLE_ENDIAN)

        #: Location of Type-M Path Table
        self.m_path_table_location: int = unpack_i32(data[148:152], endianess=Endianess.BIG_ENDIAN)

        #: Location of Optional Type-M Path Table
        self.optional_m_path_table_location: int = unpack_i32(data[152:156], endianess=Endianess.BIG_ENDIAN)

        #: The Root Directory Record
        self.root_directory_record: DirectoryRecord = DirectoryRecord(data[156:190])

        #: Volume Set Identifier
        self.volume_set_identifier: str = unpack_str_d(data[190:318])

        #: Publisher Identifier
        self.publisher_identifier: Optional[str]
        publisher_identifier_data: bytes = data[318:446]
        if publisher_identifier_data[0] == 0x5F:
            # If first byte is 0x5F, self.publisher_identifier contains file name of data in the root directory
            self.publisher_identifier = unpack_str_a(publisher_identifier_data[1:128])
        elif publisher_identifier_data == bytes([0x20] * 128):
            # If all bytes are 0x20, self.publisher_identifier is None since there is no data provided
            self.publisher_identifier = None
        else:
            raise InvalidISOException(
                f"Publisher Identifier data neither starts with 0x5F or is "
                f"128 x 0x20, instead it is: {hexlify(publisher_identifier_data)}."
            )

        #: Data Preparer Identifier
        self.data_preparer_identifier: Optional[str]
        data_preparer_identifier_data: bytes = data[446:574]
        if data_preparer_identifier_data[0] == 0x5F:
            # If first byte is 0x5F, self.data_preparer_identifier contains file name of data in the root directory
            self.data_preparer_identifier = unpack_str_a(data_preparer_identifier_data[1:128])
        elif data_preparer_identifier_data == bytes([0x20] * 128):
            # If all bytes are 0x20, self.data_preparer_identifier is None since there is no data provided
            self.data_preparer_identifier = None
        else:
            raise InvalidISOException(
                f"Data Preparer Identifier data neither starts with 0x5F or is "
                f"128 x 0x20, instead it is: {hexlify(data_preparer_identifier_data)}."
            )

        #: Application Identifier
        self.application_identifier: Optional[str]
        application_identifier_data: bytes = data[574:702]
        if application_identifier_data[0] == 0x5F:
            # If first byte is 0x5F, self.application_identifier contains file name of data in the root directory

            self.application_identifier = unpack_str_a(application_identifier_data[1:128])
        elif application_identifier_data == bytes([0x20] * 128):
            # If all bytes are 0x20, self.application_identifier is None since there is no data provided

            self.application_identifier = None
        else:
            raise InvalidISOException(
                f"Application Identifier data neither starts with 0x5F or is "
                f"128 x 0x20, instead it is: {hexlify(application_identifier_data)}."
            )

        #: Copyright File Identifier
        self.copyright_file_identifier: Optional[str]
        copyright_file_identifier_data: bytes = data[702:740]
        if copyright_file_identifier_data == bytes([0x20] * 38):
            #: If all bytes are 0x20, self.copyright_file_identifier is None since there is no data provided
            self.copyright_file_identifier = None
        else:
            self.copyright_file_identifier = unpack_str_d(copyright_file_identifier_data)

        #: Abstract File Identifier
        self.abstract_file_identifier: Optional[str]
        abstract_file_identifier_data: bytes = data[740:776]
        if abstract_file_identifier_data == bytes([0x20] * 36):
            #: If all bytes are 0x20, self.abstract_file_identifier is None since there is no data provided
            self.abstract_file_identifier = None
        else:
            self.abstract_file_identifier = unpack_str_d(abstract_file_identifier_data)

        #: Copyright File Identifier
        self.bibliographic_file_identifier: Optional[str]
        bibliographic_file_identifier_data: bytes = data[776:813]
        if copyright_file_identifier_data == bytes([0x20] * 37):
            #: If all bytes are 0x20, self.bibliographic_file_identifier is None since there is no data provided
            self.bibliographic_file_identifier = None
        else:
            self.bibliographic_file_identifier = unpack_str_d(bibliographic_file_identifier_data)

        #: Volume Creation Date and Time
        self.volume_creation_datetime: datetime = unpack_iso_volume_datetime(data[813:830])

        #: Volume Modification Date and Time
        self.volume_modification_datetime: datetime = unpack_iso_volume_datetime(data[830:847])

        #: Volume Expiration Date and Time (when is the volume considered obsolete)
        #: If not specified, then the volume is never considered obsolete
        self.volume_expiration_datetime: datetime = unpack_iso_volume_datetime(data[847:864])

        #: Volume Effective Date and Time (when may the volume start being used)
        #: If not specified, the volume may be used immediately
        self.volume_effective_datetime: datetime = unpack_iso_volume_datetime(data[864:881])

        #: File structure version (always 0x01)
        self.file_structure_version: int = data[881]
        if self.file_structure_version != 0x01:
            raise InvalidISOException(f"File Structure Version is {self.file_structure_version} instead of 0x01.")

        #: Unused field (always 0x00)
        self.unused_4: int = data[882]
        if self.unused_4 != 0x00:
            raise InvalidISOException(
                f"Unused field at index 882 should always be 0x00. Instead it is {hex(self.unused_4)}."
            )

        #: Application Specific Data
        self.application_data: bytes = data[883:1395]

        #: Reserved by ISO
        self.reserved: bytes = data[1395:2048]
