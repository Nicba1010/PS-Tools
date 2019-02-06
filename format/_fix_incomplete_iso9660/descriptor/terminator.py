from .base import BaseVolumeDescriptor


class VolumeDescriptorSetTerminator(BaseVolumeDescriptor):
    def __init__(self, data: bytes):
        super().__init__(data)
