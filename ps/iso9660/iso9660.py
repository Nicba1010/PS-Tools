import logging
import os
from typing import IO, Dict

from ps.iso9660.descriptor.base import BaseVolumeDescriptor
from ps.iso9660.descriptor.boot_record import BootRecordDescriptor
from ps.iso9660.descriptor.partition import PartitionVolumeDescriptor
from ps.iso9660.descriptor.primary import PrimaryVolumeDescriptor
from ps.iso9660.descriptor.supplementary import SupplementaryVolumeDescriptor
from ps.iso9660.descriptor.terminator import VolumeDescriptorSetTerminator
from ps.iso9660.descriptor.type import DescriptorType
from .errors import EmptyISOException

logger = logging.getLogger('ISO')


class ISO9660(object):
    def __init__(self, path: str):
        self.path: str = path

        if os.stat(self.path).st_size == 0:
            logger.error("Error, file is empty")
            raise EmptyISOException()

        with open(self.path, 'rb') as f:
            self.magic: bytes = f.read(4)

            self.compression: bool = False
            self.block_size: int = 2048

            self.volume_descriptors: Dict[DescriptorType, BaseVolumeDescriptor] = {}
            descriptor_sector = 16
            while True:
                data: bytes = self.read_sector(f, descriptor_sector)
                volume_descriptor: BaseVolumeDescriptor = self.create_descriptor(data)
                if volume_descriptor.standard_identifier == "CD001":
                    descriptor_sector += 1
                else:
                    break
                if volume_descriptor.descriptor_type not in self.volume_descriptors:
                    self.volume_descriptors[volume_descriptor.descriptor_type] = volume_descriptor

        a = 4

    @staticmethod
    def create_descriptor(data: bytes) -> BaseVolumeDescriptor:
        base_volume_descriptor: BaseVolumeDescriptor = BaseVolumeDescriptor(data)
        if base_volume_descriptor.descriptor_type == DescriptorType.PRIMARY:
            return PrimaryVolumeDescriptor(data)
        elif base_volume_descriptor.descriptor_type == DescriptorType.SUPPLEMENTARY:
            return SupplementaryVolumeDescriptor(data)
        elif base_volume_descriptor.descriptor_type == DescriptorType.TERMINATOR:
            return VolumeDescriptorSetTerminator(data)
        elif base_volume_descriptor.descriptor_type == DescriptorType.PARTITION:
            return PartitionVolumeDescriptor(data)
        elif base_volume_descriptor.descriptor_type == DescriptorType.BOOT_RECORD:
            return BootRecordDescriptor(data)
        else:
            raise Exception

    def read_sector(self, f: IO, sector: int) -> bytes:
        if not self.compression:
            f.seek(self.block_size * sector)
            return f.read(self.block_size)
