from format._fix_incomplete_iso9660.errors import InvalidISOException
from format._fix_incomplete_iso9660.utils import unpack_str_a, unpack_str_d, unpack_both_endian_i32
from .base import BaseVolumeDescriptor


class PartitionVolumeDescriptor(BaseVolumeDescriptor):
    def __init__(self, data: bytes):
        super().__init__(data)

        #: Unused Field (Always 0x00)
        self.unused_1: int = data[7]
        if self.unused_1 != 0x00:
            raise InvalidISOException(
                f"Unused field at index 7 should always be 0x00. Instead it is {hex(self.unused_1)}."
            )

        #: The System Identifier
        self.system_identifier: str = unpack_str_a(data[8:40])

        #: The Volume Identifier
        self.volume_identifier: str = unpack_str_d(data[40:72])

        #: Volume Partition Location
        self.volume_partition_location: int = unpack_both_endian_i32(data[72:80])

        #: Volume Partition Size
        self.volume_partition_size: int = unpack_both_endian_i32(data[80:88])

        #: System Use
        self.system_use: bytes = data[88:2048]
