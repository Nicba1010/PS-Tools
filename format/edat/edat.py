from base.file_format import FileFormatWithMagic
from .header import EDATHeader


class EDAT(FileFormatWithMagic[EDATHeader]):
    def __init__(self, path: str):
        super().__init__(path, EDATHeader)
