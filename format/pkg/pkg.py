import hashlib
import os
from typing import List, Optional

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes, CipherContext

from base.file_format import FileFormatWithMagic
from format.pkg.metadata import ContentTypeMetadata
from format.pkg.type import PkgType
from utils.keys import PS3_GPKG_KEY, PSP_GPKG_KEY, PSP2_GPKG_KEY0, PSP2_GPKG_KEY1, PSP2_GPKG_KEY2
from utils.utils import DEFAULT_LOCAL_IO_BLOCK_SIZE, backend
from .content_type import ContentType
from .decryptor import PkgInternalIO
from .drm_type import DrmType
from .entry import PKGEntry
from .errors import InvalidPKGHeaderHashException
from .header import PkgHeader
from .metadata import PkgMetadata
from .revision import PkgRevision


class PKG(FileFormatWithMagic[PkgHeader]):

    def __init__(self, path: str, verify: bool = True):
        super().__init__(path, PkgHeader, verify)

        sha1 = hashlib.sha1()
        self.file_handle.seek(0x00)
        sha1.update(self.file_handle.read(0x80))

        # TODO: Why DEBUG pkg hash always fail?
        if sha1.digest()[-8:] != self.header.header_sha1_hash and self.header.revision != PkgRevision.DEBUG:
            raise InvalidPKGHeaderHashException()
        else:
            self.logger.info('Header SHA1 Hash Verified!')

        self.drm_type: DrmType = None
        self.content_type: ContentType = None
        self.system_version: str = None
        self.app_version: str = None
        self.package_version: str = None
        self.make_package_npdrm_rev: int = None
        self.title_id: str = None
        self.qa_digest: bytes = None

        self.metadata: List[PkgMetadata] = []
        self.file_handle.seek(self.header.metadata_offset)

        for metadata_index in range(0, self.header.metadata_count):
            self.logger.info(f'Processing metadata #{metadata_index}:')
            self.metadata.append(PkgMetadata.create(self.file_handle))

        self.file_handle.seek(self.header.data_offset)
        self.files: List[PKGEntry] = []
        with PkgInternalIO(self.file_handle, self.header, self.internal_fs_key) as fd:
            for item_index in range(0, self.header.item_count):
                self.logger.info(f'Processing file #{item_index}:')
                self.file_handle.seek(self.header.data_offset + PKGEntry.size() * item_index)
                self.files.append(PKGEntry(fd))

    @property
    def internal_fs_key(self) -> bytes:
        if self.header.type == PkgType.PS3:
            return PS3_GPKG_KEY
        else:
            for metadata in self.metadata:
                if isinstance(metadata, ContentTypeMetadata):
                    encryption_key: Optional[bytes] = None

                    if metadata.content_type == ContentType.PSP2GD:
                        encryption_key = PSP2_GPKG_KEY0
                    elif metadata.content_type == ContentType.PSP2AC:
                        encryption_key = PSP2_GPKG_KEY1
                    elif metadata.content_type == ContentType.PSP2LA:
                        encryption_key = PSP2_GPKG_KEY2

                    if encryption_key is not None:
                        cipher: Cipher = Cipher(algorithms.AES(encryption_key), modes.ECB(), backend=backend)
                        encryptor: CipherContext = cipher.encryptor()
                        return encryptor.update(self.header.pkg_data_riv)
            return PSP_GPKG_KEY

    def verify_hash(self) -> bool:
        with open(self.path, 'rb') as f:
            size_without_pkg_hash = os.stat(self.path).st_size - 32
            f.seek(size_without_pkg_hash)

            pkg_hash: bytes = f.read(20)

            sha1 = hashlib.sha1()
            f.seek(0x00)

            to_read: int = size_without_pkg_hash
            while to_read > 0:
                data: bytes = f.read(to_read if to_read < DEFAULT_LOCAL_IO_BLOCK_SIZE else DEFAULT_LOCAL_IO_BLOCK_SIZE)
                sha1.update(data)
                to_read -= len(data)

            return pkg_hash == sha1.digest()
