import hashlib
import os
from io import BytesIO
from typing import List

from clint.textui import puts, indent

from ps.file.format.pkg import PkgRevision
from ps.utils import DEFAULT_LOCAL_IO_BLOCK_SIZE
from .content_type import ContentType
from .decryptor import DecryptorIO
from .drm_type import DrmType
from .entry import PkgEntry
from .errors import InvalidPKGHeaderHashException, EmptyPKGException, InvalidPKGHashException
from .header import PkgHeader
from .metadata import PkgMetadata


class Pkg(object):

    def __init__(self, path: str, verify_pkg_hash: bool = True):
        self.path: str = path
        if os.stat(self.path).st_size == 0:
            raise EmptyPKGException()

        self.file_handle: BytesIO = open(self.path, 'rb')

        self.header: PkgHeader = PkgHeader(self.file_handle)
        sha1 = hashlib.sha1()
        self.file_handle.seek(0x00)
        sha1.update(self.file_handle.read(0x80))

        # TODO: Why DEBUG pkg always fail?
        if sha1.digest()[-8:] != self.header.header_sha1_hash and self.header.revision != PkgRevision.DEBUG:
            raise InvalidPKGHeaderHashException()
        else:
            puts("Header SHA1 Hash Verified!")

        if verify_pkg_hash:
            if not self.verify():
                raise InvalidPKGHashException()
            else:
                puts("PKG SHA1 Hash Verified!")

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
            puts("Processing metadata on index {}:".format(metadata_index))
            with indent(4, '>>>'):
                self.metadata.append(PkgMetadata.create(self.file_handle))

        self.file_handle.seek(self.header.data_offset)
        self.files: List[PkgEntry] = []
        with DecryptorIO(self.header, self.file_handle) as fd:
            for item_index in range(0, self.header.item_count):
                puts("Processing item on index {}:".format(item_index))
                with indent(4, '>>>'):
                    self.file_handle.seek(self.header.data_offset + PkgEntry.size() * item_index)
                    self.files.append(PkgEntry(fd))

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

    def __del__(self):
        puts('Cleaning up...')
        if not self.file_handle.closed:
            self.file_handle.close()
