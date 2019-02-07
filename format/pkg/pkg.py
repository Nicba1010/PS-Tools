import hashlib
import os
from typing import List

from base.file_format import FileFormatWithMagic
from utils.utils import DEFAULT_LOCAL_IO_BLOCK_SIZE
from .content_type import ContentType
from .decryptor import DecryptorIO
from .drm_type import DrmType
from .entry import PKGEntry
from .errors import InvalidPKGHeaderHashException, InvalidPKGHashException
from .header import PkgHeader
from .metadata import PkgMetadata
from .revision import PkgRevision


class PKG(FileFormatWithMagic[PkgHeader]):

    def __init__(self, path: str, verify_pkg_hash: bool = True):
        super().__init__(path, PkgHeader)

        sha1 = hashlib.sha1()
        self.file_handle.seek(0x00)
        sha1.update(self.file_handle.read(0x80))

        # TODO: Why DEBUG pkg hash always fail?
        if sha1.digest()[-8:] != self.header.header_sha1_hash and self.header.revision != PkgRevision.DEBUG:
            raise InvalidPKGHeaderHashException()
        else:
            self.logger.info('Header SHA1 Hash Verified!')

        if verify_pkg_hash:
            if not self.verify():
                raise InvalidPKGHashException()
            else:
                self.logger.info('PKG SHA1 Hash Verified!')

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
        with DecryptorIO(self.header, self.file_handle) as fd:
            for item_index in range(0, self.header.item_count):
                self.logger.info(f'Processing file #{item_index}:')
                self.file_handle.seek(self.header.data_offset + PKGEntry.size() * item_index)
                self.files.append(PKGEntry(fd))

    def verify(self) -> bool:
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
