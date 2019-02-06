import logging
import math
import os
from typing import IO, Dict

from .descriptor import BaseVolumeDescriptor
from .descriptor import BootRecordDescriptor
from .descriptor import DescriptorType
from .descriptor import PartitionVolumeDescriptor
from .descriptor import PrimaryVolumeDescriptor
from .descriptor import SupplementaryVolumeDescriptor
from .descriptor import VolumeDescriptorSetTerminator
from .errors import EmptyISOException
from .path_table_record import PathTableRecord

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
            self.path_tables: Dict[DescriptorType, Dict[str, PathTableRecord]] = {}
            descriptor_sector = 16
            while True:
                descriptor_data: bytes = self.read_sector(f, descriptor_sector)
                volume_descriptor: BaseVolumeDescriptor = self.create_descriptor(descriptor_data)
                if volume_descriptor.standard_identifier == "CD001":
                    descriptor_sector += 1
                else:
                    break
                if volume_descriptor.descriptor_type not in self.volume_descriptors:
                    self.volume_descriptors[volume_descriptor.descriptor_type] = volume_descriptor
                    if isinstance(volume_descriptor, PrimaryVolumeDescriptor):
                        path_table_data: bytes = self.read_sector(
                            f=f,
                            sector=volume_descriptor.l_path_table_location,
                            sector_count=math.ceil(
                                volume_descriptor.path_table_size / volume_descriptor.logical_block_size
                            )
                        )
                        path_table_offset: int = 0
                        while path_table_offset < volume_descriptor.path_table_size:
                            path_table_record: PathTableRecord = PathTableRecord(path_table_data[path_table_offset:])
                            path_table_offset += path_table_record.size

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

    def read_sector(self, f: IO, sector: int, sector_count: int = 1) -> bytes:
        if not self.compression:
            f.seek(self.block_size * sector)
            return f.read(self.block_size * sector_count)
