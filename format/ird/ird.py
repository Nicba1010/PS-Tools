import gzip
import zlib
from binascii import hexlify
from typing import IO, List, Dict

from base.file_format import FileFormatWithMagic
from utils.utils import read_u8, read_u32, unpack_u32, Endianess
from .constants import compressed_magic, data2_patch_decryptor, data2_patch_encryptor
from .errors import InvalidIRDCRCException
from .header import IRDHeader


class IRD(FileFormatWithMagic[IRDHeader]):
    def __init__(self, path: str, verify=True):
        super().__init__(path, IRDHeader)

        if self.version == 7:
            self.id: str = read_u32(self.file_handle)
            self.logger.debug(f"ID (v7 only): {self.id}")

        #: ISO9660 Header Size
        self.iso_header_size: int = read_u32(self.file_handle, endianess=Endianess.LITTLE_ENDIAN)
        self.logger.debug(f"Header Size: {self.iso_header_size}")

        # TODO: Write ISO9660 Header Parser
        #: ISO9660 Header
        self.iso_header: bytes = zlib.decompress(self.file_handle.read(self.iso_header_size), 15 + 16)

        #: ISO9660 Footer Size
        self.iso_footer_size: int = read_u32(self.file_handle, endianess=Endianess.LITTLE_ENDIAN)
        self.logger.debug(f"Footer Size: {self.iso_footer_size}")

        # TODO: Write ISO9660 Footer Parser
        #: ISO9660 Footer
        self.iso_footer: IO = gzip.GzipFile(fileobj=self.file_handle.read(self.iso_footer_size))

        #: TODO: Document this!
        self.region_count: int = read_u8(self.file_handle)
        self.logger.debug(f"Region Count: {self.region_count}")

        #: TODO: Document this!
        self.region_hashes: List[bytes] = []
        for i in range(0, self.region_count):
            region_hash: bytes = self.file_handle.read(16)
            self.region_hashes.append(region_hash)
            self.logger.debug(f"Region {i} hash: {hexlify(region_hash)}")

        #: Number of file hash entries
        self.file_count: int = read_u32(self.file_handle, endianess=Endianess.LITTLE_ENDIAN)
        self.logger.debug(f"File Count: {self.file_count}")

        #: File Key -> File Hash map
        self.file_map: Dict[bytes, bytes] = {}
        for i in range(0, self.file_count):
            file_key: bytes = self.file_handle.read(8)
            file_hash: bytes = self.file_handle.read(16)
            self.file_map[file_key] = file_hash
            self.logger.debug(f"File {i}: {hexlify(file_key)} -> {hexlify(file_hash)}")

        #: 4 byte padding
        self.padding: bytes = self.file_handle.read(4)

        if self.version >= 9:
            #: See http://www.t10.org/ftp/t10/document.04/04-328r0.pdf#page=43
            self.pic: bytes = self.file_handle.read(115)
            self.logger.debug(f"PIC: {hexlify(self.pic).decode('ASCII')}")

        #: Used to derive the disc AES encryption key
        self.data1: bytes = self.file_handle.read(16)
        #: TODO: Document this!
        self.data2: bytes = self.file_handle.read(16)
        #: Data2 Decrypted
        self.data2_decrypted: bytes = IRD.decrypt_data2(self.data2)
        #: Data2 Patched
        self.data2_patched: bytes = IRD.patch_data2(self.data2)
        self.logger.info(f"Data1: {hexlify(self.data1).decode('ASCII')}")
        self.logger.info(f"Data2: {hexlify(self.data2).decode('ASCII')}")
        self.logger.info(f"Data2(decrypted): {hexlify(self.data2_decrypted).decode('ASCII')}")
        self.logger.info(f"Data2(patched): {hexlify(self.data2_patched).decode('ASCII')}")

        if self.version < 9:
            #: See http://www.t10.org/ftp/t10/document.04/04-328r0.pdf#page=43
            self.pic: bytes = self.file_handle.read(115)
            self.logger.debug(f"PIC: {hexlify(self.pic).decode('ASCII')}")

        if self.version > 7:
            #: TODO: Document this!
            self.uid: str = read_u32(self.file_handle, endianess=Endianess.LITTLE_ENDIAN)
            self.logger.debug(f"UID: {self.uid}")

        if verify and self.verify(self.file_handle):
            self.logger.info(f"CRC Verified")
        else:
            raise InvalidIRDCRCException()

        self.logger.info(f"File successfully parsed")

    def get_file_handle(self) -> IO:
        """
        Returns a file handle depending on if the IRD file
        is gzip compressed, or already extracted.
        :return: file handle
        """
        with open(self.path, 'rb') as f:
            tmp_magic: bytes = f.read(4)
        if tmp_magic == compressed_magic:
            return gzip.open(self.path, 'rb')
        else:
            return super().get_file_handle()

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
        crc: int = read_u32(f, endianess=Endianess.LITTLE_ENDIAN)
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

    @staticmethod
    def decrypt_data2(data2: bytes) -> bytes:
        """
        Decrypts data2 using the data2_key and data2_iv
        with AES in CBC mode (constants.py).
        :param data2: data2
        :return: decrypted data2
        """
        return data2_patch_decryptor.update(data2)

    @staticmethod
    def patch_data2(data2: bytes) -> bytes:
        """
        Patches data2.
        Steps:
         - Decrypt data2
         - Swap last 4 bytes
         - Encrypt with same keys used for decrypting data2
        :param data2: data2
        :return: patched data2
        """
        data2_decrypted: bytes = IRD.decrypt_data2(data2)
        if unpack_u32(data2_decrypted[12:16]) == 1:
            data2_decrypted_patch: bytes = data2_decrypted[0:12] + bytes([0x01, 0x00, 0x00, 0x00])
            data2_decrypted_patch = data2_patch_encryptor.update(data2_decrypted_patch)
            return data2_decrypted_patch
        else:
            return data2
