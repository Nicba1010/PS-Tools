from aenum import Enum


class PkgType(Enum):
    PS3 = bytes([0x00, 0x01])
    PSP_PSVITA = bytes([0x00, 0x02])
