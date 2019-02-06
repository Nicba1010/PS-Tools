from format._fix_incomplete_iso9660.descriptor import BaseVolumeDescriptor
from format._fix_incomplete_iso9660.utils import unpack_str_a


class BootRecordDescriptor(BaseVolumeDescriptor):
    def __init__(self, data: bytes):
        super().__init__(data)

        #: Boot System Identifier (ID of the system capable of booting from this boot record)
        self.boot_system_identifier: str = unpack_str_a(data[7:39])

        #: Boot Identifier (Identification the the boot system defined in the rest of this descriptor)
        self.boot_identifier: str = unpack_str_a(data[39:71])

        #: Boot System Use (Data used by the boot system)
        self.boot_system_use: bytes = data[71:2048]
