from aenum import MultiValueEnum


class EntryType(MultiValueEnum):
    NPDRM = 0x01
    NPDRM_EDAT = 0x02
    REGULAR = 0x03
    FOLDER = 0x04
    UNKNOWN_FILE = 0x06, 0x0E, 0x10, 0x11, 0x13, 0x15, 0x16
    UNKNOWN_FOLDER = 0x12
    SDAT = 0x09

    @property
    def is_file(self):
        if self in [EntryType.NPDRM, EntryType.NPDRM_EDAT, EntryType.REGULAR, EntryType.UNKNOWN_FILE, EntryType.SDAT]:
            return True
        elif self in [EntryType.FOLDER, EntryType.UNKNOWN_FOLDER]:
            return False
