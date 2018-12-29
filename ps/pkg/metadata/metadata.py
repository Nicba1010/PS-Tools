import struct
from binascii import hexlify
from typing import IO, List

from clint.textui import puts

from ps.pkg.content_type import ContentType
from ps.pkg.drm_type import DrmType
from ps.pkg.errors import InvalidPKGException, InvalidPKGMetadataSizeException, InvalidPKGMetadataException


class PkgMetadata(object):
    id: int = NotImplementedError
    category_name: str = NotImplementedError
    possible_sizes: List[int] = NotImplementedError
    possible_values: List[bytes] = NotImplementedError

    def __init__(self, f: IO):
        self.id = struct.unpack('>I', f.read(4))[0]
        self.data_size = struct.unpack('>I', f.read(4))[0]
        self.data = f.read(self.data_size)
        puts("Type: {}".format(self.category_name))
        puts("Identifier: {}".format(self.id))
        puts("Data Size: {}".format(self.data_size))
        puts("Data: {}".format(hexlify(self.data)))

        if len(self.possible_sizes) != 0 and self.data_size not in self.__class__.possible_sizes:
            raise InvalidPKGMetadataSizeException(self.data_size, self.possible_sizes)

        if len(self.possible_values) != 0 and self.data not in self.__class__.possible_values:
            raise InvalidPKGMetadataException(self.data, self.possible_values)

    @staticmethod
    def create(f: IO) -> 'PkgMetadata':
        id: int = struct.unpack('>I', f.read(4))[0]
        f.seek(f.tell() - 4)
        for subclass in PkgMetadata.__subclasses__():
            if subclass.id == id:
                return subclass(f)
        raise InvalidPKGException


class DrmTypeMetadata(PkgMetadata):
    id = 0x01
    category_name = "DRM Type"
    possible_sizes = [0x04]
    possible_values = list(bytes([0x00, 0x00, 0x00, i]) for i in range(0, 0xF))

    def __init__(self, f: IO):
        super().__init__(f)
        self.drm_type: DrmType = DrmType(struct.unpack('>I', self.data)[0])
        puts("Drm Type: {}".format(self.drm_type))


class ContentTypeMetadata(PkgMetadata):
    id = 0x02
    category_name = "Content Type"
    possible_sizes = [0x04]
    possible_values = list(bytes([0x00, 0x00, 0x00, i]) for i in range(0, 0x1A)) + [
        bytes([0x00, 0x00, 0x00, 0x1D]),
        bytes([0x00, 0x00, 0x00, 0x1F])
    ]

    def __init__(self, f: IO):
        super().__init__(f)
        self.content_type: ContentType = ContentType(struct.unpack('>I', self.data)[0])
        puts("Content Type: {}".format(self.content_type))

    @property
    def install_path(self) -> str:
        return self.content_type.install_path


class PackageTypeMetadata(PkgMetadata):
    id = 0x03
    category_name = "Package Type"
    possible_sizes = [0x04]
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        # TODO: Wiki....


class PackageSizeMetadata(PkgMetadata):
    id = 0x04
    category_name = "Package Size"
    possible_sizes = [0x08]
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        self.package_size: int = struct.unpack('>Q', self.data)[0]
        puts("Package Size: {}".format(self.package_size))


class PkgMetaDataMetadata(PkgMetadata):
    id = 0x05
    category_name = "make_package_npdrm Revision (2 bytes) + Package Version (2 bytes)"
    possible_sizes = [0x04]
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        self.make_package_npdrm_rev = struct.unpack('>H', self.data[0:2])[0]
        self.package_version = "{}.{}".format(
            hexlify(self.data[2:3]).decode("utf-8"),
            hexlify(self.data[3:4]).decode("utf-8")
        )
        puts("Make Package NPDRM Revision: {}".format(self.make_package_npdrm_rev))
        puts("Package Version: {}".format(self.package_version))


class TitleIdMetadata(PkgMetadata):
    id = 0x06
    category_name = "Version + App Version / TitleID (on size 0xC)"
    possible_sizes = [0x0C]
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        self.title_id = str(self.data)
        puts("Title ID: {}".format(self.title_id))


class QADigestMetadata(PkgMetadata):
    id = 0x07
    category_name = "QA Digest"
    possible_sizes = [0x18]
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        self.qa_digest = self.data
        puts("QA Digest: {}".format(hexlify(self.qa_digest)))


class VersionMetadata(PkgMetadata):
    id = 0x08
    category_name = "unk (1 byte) + " \
                    "PS3/PSP/PSP2 System Version (3 bytes) + " \
                    "Package Version (2 bytes) + App Version (2 bytes)"
    possible_sizes = [0x08]
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        # TODO: Investigate what this is
        self.unk: int = struct.unpack('>B', self.data[0:1])[0]
        self.system_version: str = "{}.{}".format(
            hexlify(self.data[1:2]).decode("utf-8"),
            hexlify(self.data[2:4]).decode("utf-8")
        )
        self.app_version: str = "{}.{}".format(
            hexlify(self.data[6:7]).decode("utf-8"),
            hexlify(self.data[7:8]).decode("utf-8")
        )
        self.package_version: str = "{}.{}".format(
            hexlify(self.data[4:5]).decode("utf-8"),
            hexlify(self.data[5:6]).decode("utf-8")
        )
        puts("System Version: {}".format(self.system_version))
        puts("Package Version: {}".format(self.package_version))
        puts("App Version: {}".format(self.app_version))


class UnknownMetadata(PkgMetadata):
    id = 0x09
    category_name = "Unknown"
    possible_sizes = [0x08]
    possible_values = [
        bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
        bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x24, 0x00, 0x00]),
        bytes([0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00]),
        bytes([0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00]),
        bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00]),
        bytes([0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00]),
        bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00]),
        bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00])
    ]

    def __init__(self, f: IO):
        super().__init__(f)
        # TODO: Investigate what this is
        puts("Unknown: {}".format(hexlify(self.data)))


class InstallDirectoryMetadata(PkgMetadata):
    id = 0x0A
    category_name = "Install Directory"
    possible_sizes = [0x28]
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        self.install_directory: str = self.data.decode('utf-8')
        puts("Install Directory: {}".format(self.install_directory))


class Unknown2Metadata(PkgMetadata):
    id = 0x0B
    category_name = "Unknown (seen in PSP cumulative patch)"
    possible_sizes = [0x08]
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        # TODO: Investigate what this is
        puts("Unknown (seen in PSP cumulative patch): {}".format(hexlify(self.data)))


class Unknown3Metadata(PkgMetadata):
    id = 0x0C
    category_name = "Unknown"
    possible_sizes = []
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        # TODO: Investigate what this is
        puts("Unknown: {}".format(hexlify(self.data)))


class IndexTableMetadata(PkgMetadata):
    id = 0x0D
    category_name = "index_table_info"
    possible_sizes = [0x28]
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        raise NotImplementedError


class ParamSFOMetadata(PkgMetadata):
    id = 0x0E
    category_name = "PARAM.SFO Info"
    possible_sizes = [0x38]
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        raise NotImplementedError


class UnknownDataMetadata(PkgMetadata):
    id = 0x0F
    category_name = "unknown_data_info"
    possible_sizes = [0x48]
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        raise NotImplementedError


class EntiretyMetadata(PkgMetadata):
    id = 0x10
    category_name = "Entirety Info"
    possible_sizes = [0x38]
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        raise NotImplementedError


class PublishingMetadata(PkgMetadata):
    id = 0x11
    category_name = "PublishingTools version (4 Bytes) + " \
                    "PFSBuilder version (4 Bytes) + " \
                    "padding (0x20 Bytes)"
    possible_sizes = [0x28]
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        raise NotImplementedError


class SelfMetadata(PkgMetadata):
    id = 0x12
    category_name = "self_info"
    possible_sizes = [0x38]
    possible_values = []

    def __init__(self, f: IO):
        super().__init__(f)
        raise NotImplementedError
