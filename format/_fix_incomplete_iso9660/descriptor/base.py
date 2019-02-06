from format._fix_incomplete_iso9660.utils import unpack_str_a
from .type import DescriptorType


class BaseVolumeDescriptor(object):
    def __init__(self, data: bytes):
        self.data: bytes = data

        self.descriptor_type: DescriptorType = DescriptorType(self.data[0])
        self.standard_identifier: str = unpack_str_a(self.data[1:6])
        self.version: int = self.data[6]

    @property
    def encoding(self):
        if self.descriptor_type == DescriptorType.SUPPLEMENTARY:
            return 'UTF-8'
        else:
            return 'ASCII'
