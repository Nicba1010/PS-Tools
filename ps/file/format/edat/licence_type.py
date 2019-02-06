from aenum import Enum


class LicenceType(Enum):
    DEBUG_SDAT = 0x00
    NETWORK_LICENCE = 0x01
    LOCAL_LICENCE = 0x02
    FREE_LICENCE = 0x03
