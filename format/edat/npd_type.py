from aenum import Enum


class NpdType(Enum):
    FINALIZED_EDAT = 0x00
    FINALIZED_SDAT = 0x01
    NON_FINALIZED_EDAT = 0x80
    NON_FINALIZED_SDAT = 0x81
