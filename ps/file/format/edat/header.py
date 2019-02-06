import logging
from binascii import hexlify
from typing import IO

from ps.utils import read_u32, Endianess, read_u8, unpack_u32, read_u64
from .application_type import ApplicationType
from .constants import magic
from .errors import InvalidEDATMagicException, InvalidEDATBlockSizeException
from .licence_type import LicenceType
from .metadata_type import MetadataType
from .npd_type import NpdType

GAME_ID_SIZE = 0x09

logger = logging.getLogger('EDAT Header')


class EDATHeader(object):
    def __init__(self, f: IO):
        #: EDAT magic string, should be: NPD\0
        self.magic: bytes = f.read(4)
        logger.info("EDAT Magic: {}".format(self.magic))

        if self.magic != magic:
            logger.error("Error, invalid magic")
            raise InvalidEDATMagicException
        else:
            logger.info("Magic Verified")

        #: EDAT file format version
        self.version: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        logger.info(f"EDAT Version: {self.version}")

        #: Licence Type
        self.licence_type: LicenceType = LicenceType(read_u32(f, endianess=Endianess.BIG_ENDIAN))
        logger.info(f"Licence Type: {self.licence_type}")

        #: Application Type
        self.application_type: ApplicationType = ApplicationType(read_u32(f, endianess=Endianess.BIG_ENDIAN))
        logger.info(f"Application Type: {self.application_type}")

        #: Content ID
        self.content_id: str = f.read(0x30).decode('UTF-8')
        logger.info(f"Content ID: {self.content_id}")

        #: Digest
        """
         (seems like to be a SHA-1 hash of the non-finalized file)
         hash of the original data which is unknown until the whole 
         file is read, can not be used as check. Can be used as 
         watermark or zeroed on forged file.
        """
        # TODO: Do hashcheck
        self.qa_digest: bytearray = f.read(0x10)
        logger.info(f"QA Digest: {hexlify(self.qa_digest)}")

        #: NPD Hash 1
        """
         CID-FN hash (an AES CMAC hash of concatenation of Content
         ID and File Name using the third NPDRM OMAC key as CMAC key)
        """
        # TODO: Do hashcheck
        self.npd_hash_1: bytearray = f.read(0x10)
        logger.info(f"NPD Hash 1: {hexlify(self.npd_hash_1)}")

        #: NPD Hash 2
        """
         header hash (an AES CMAC hash of the 0x60 bytes from the 
         beginning of file using xored bytes of the developer's 
         klicensee and the second NPDRM OMAC key as CMAC key)
        """
        # TODO: Do hashcheck
        self.npd_hash_2: bytearray = f.read(0x10)
        logger.info(f"NPD Hash 2: {hexlify(self.npd_hash_2)}")

        #: Activation Time (start of the validity period, filled with 0x00 if not used)
        # TODO: Reverse date format
        self.activation_time: bytearray = f.read(0x08)
        logger.info(f"Activation Time: {hexlify(self.activation_time)}")

        #: Deactivation Time (end of the validity period, filled with 0x00 if not used)
        # TODO: Reverse date format
        self.deactivation_time: bytearray = f.read(0x08)
        logger.info(f"Deactivation Time: {hexlify(self.deactivation_time)}")

        #: Npd Type
        # TODO: (Separated from Metadata type for wiki format)
        self.npd_type: NpdType = NpdType(read_u8(f, endianess=Endianess.BIG_ENDIAN))
        logger.info(f"Npd Type: {self.npd_type}")

        #: Metadata Type
        # TODO: (Outdated Flags description from talk page)
        self.metadata_type: MetadataType = MetadataType(
            unpack_u32(bytes([0]) + f.read(0x03), endianess=Endianess.BIG_ENDIAN)
        )
        logger.info(f"Metadata Type: {self.metadata_type}")

        #: Block Size
        self.block_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        logger.info(f"Block Size: {self.block_size}")
        if self.block_size > 0x8000:
            raise InvalidEDATBlockSizeException()

        #: Data Size
        self.data_size: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        logger.info(f"Data Size: {self.data_size}")

        #: Metadata Sections Hash
        # TODO: Do hashcheck
        self.metadata_sections_hash: bytearray = f.read(0x10)
        logger.info(f"Metadata Sections Hash: {hexlify(self.metadata_sections_hash)}")

        #: Extended Header Hash
        """
         An AES CMAC hash of 160 bytes from the beginning of file) 
         uses the hash key as CMAC key and it depends on the file 
         flags and keys
        """
        # TODO: Do hashcheck
        self.extended_header_hash: bytearray = f.read(0x10)
        logger.info(f"Extended Header Hash: {hexlify(self.extended_header_hash)}")

        #: ECDSA Metadata Signature
        """
         Can be zeroed on forged file. curve_type is vsh type 0x02, 
         pub is vsh public key,
        """
        # TODO: Do hashcheck
        self.ecdsa_metadata_signature: bytearray = f.read(0x28)
        logger.info(f"Extended Header Hash: {hexlify(self.ecdsa_metadata_signature)}")

        #: ECDSA Header Signature
        """
         Enabled (only?) for PS2 classic: all custom firmwares are 
         patched to skip the ECDSA check. Can be zeroed on forged file. 
         curve_type is vsh type 0x02, pub is vsh public key.
        """
        # TODO: Do hashcheck
        self.ecdsa_header_signature: bytearray = f.read(0x28)
        logger.info(f"ECDSA Header Signature: {hexlify(self.ecdsa_header_signature)}")
