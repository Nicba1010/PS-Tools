import gzip
import logging
import os
import zlib
from binascii import hexlify
from typing import IO, List, Dict

from ps.utils import read_u8, read_u32
from .constants import compressed_magic, uncompressed_magic
from .errors import EmptyIRDException, InvalidIRDMagicException, InvalidIRDCRCException
from .header import IRDHeader

logger = logging.getLogger('IRD')


class IRD(object):

    def __init__(self, path: str, verify=True):
        #: IRD File Path
        self.path: str = path

        logger.info(f"Parsing file: {self.path}")

        if os.stat(self.path).st_size == 0:
            logger.error("Error, file is empty")
            raise EmptyIRDException()

        with open(self.path, 'rb') as f:
            self.magic: bytes = f.read(4)

        with self.get_file_handle() as f:
            #: IRD file header
            self.header: IRDHeader = IRDHeader(f)

            if self.version == 7:
                self.id: str = read_u32(f)
                logger.debug(f"ID (v7 only): {self.id}")

            #: TODO: Document this!
            self.iso_header_size: int = read_u32(f, endianess='<')
            #: TODO: Document this!
            self.iso_header: IO = gzip.GzipFile(fileobj=f.read(self.iso_header_size))
            logger.debug(f"Header Size: {self.iso_header_size}")

            #: TODO: Document this!
            self.iso_footer_size: int = read_u32(f, endianess='<')
            #: TODO: Document this!
            self.iso_footer: IO = gzip.GzipFile(fileobj=f.read(self.iso_footer_size))
            logger.debug(f"Footer Size: {self.iso_footer_size}")

            #: TODO: Document this!
            self.region_count: int = read_u8(f)
            logger.debug(f"Region Count: {self.region_count}")

            #: TODO: Document this!
            self.region_hashes: List[bytes] = []
            for i in range(0, self.region_count):
                region_hash: bytes = f.read(16)
                self.region_hashes.append(region_hash)
                logger.debug(f"Region {i} hash: {hexlify(region_hash)}")

            #: Number of file hash entries
            self.file_count: int = read_u32(f, endianess='<')
            logger.debug(f"File Count: {self.file_count}")

            #: File Key -> File Hash map
            self.file_map: Dict[bytes, bytes] = {}
            for i in range(0, self.file_count):
                file_key: bytes = f.read(8)
                file_hash: bytes = f.read(16)
                self.file_map[file_key] = file_hash
                logger.debug(f"File {i}: {hexlify(file_key)} -> {hexlify(file_hash)}")

            #: 4 byte padding
            self.padding: bytes = f.read(4)

            if self.version >= 9:
                #: See http://www.t10.org/ftp/t10/document.04/04-328r0.pdf#page=43
                self.pic: bytes = f.read(115)
                logger.debug(f"PIC: {hexlify(self.pic).decode('ASCII')}")

            #: Used to derive the disc AES encryption key
            self.data_1: bytes = f.read(16)
            #: TODO: Document this!
            self.data_2: bytes = f.read(16)
            logger.debug(f"Data1: {hexlify(self.data_1).decode('ASCII')}")
            logger.debug(f"Data2: {hexlify(self.data_2).decode('ASCII')}")

            if self.version < 9:
                #: See http://www.t10.org/ftp/t10/document.04/04-328r0.pdf#page=43
                self.pic: bytes = f.read(115)
                logger.debug(f"PIC: {hexlify(self.pic).decode('ASCII')}")

            if self.version > 7:
                #: TODO: Document this!
                self.uid: str = read_u32(f, endianess='<')
                logger.debug(f"UID: {self.uid}")

            if verify and self.verify(f):
                logger.info(f"CRC Verified")
            else:
                raise InvalidIRDCRCException()
        logger.info(f"File successfully parsed")

    def get_file_handle(self) -> IO:
        if self.magic == compressed_magic:
            return gzip.open(self.path, 'rb')
        elif self.magic == uncompressed_magic:
            return open(self.path, 'rb')
        else:
            raise InvalidIRDMagicException()

    @staticmethod
    def verify(f: IO) -> bool:
        """
        Verifies the uncompressed data with the help of the
        last 4 bytes of the file that contain the CRC value.
        The file needs to be fully read, excluding the last
        4 bytes, for this to work.
        :param f: the file handle
        :return: if declared CRC matches computed CRC
        """
        total_bytes_no_crc: int = f.tell()
        crc: int = read_u32(f, endianess='<')
        f.seek(0)
        computed_crc = zlib.crc32(f.read(total_bytes_no_crc))
        return crc == computed_crc

    @property
    def version(self) -> int:
        """
        Gets the IRD file format version.
        :return: ird file format version
        """
        return self.header.version