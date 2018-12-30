import logging
from typing import IO

from ps.utils import read_u8
from .constants import uncompressed_magic
from .errors import InvalidIRDException

GAME_ID_SIZE = 0x09

logger = logging.getLogger('IRD Header')

class IRDHeader(object):
    def __init__(self, f: IO):
        #: IRD magic string, should be: 3IRD
        self.magic: bytes = f.read(4)
        logger.info("IRD Magic: {}".format(self.magic))

        if self.magic != uncompressed_magic:
            logger.error("Error, invalid magic")
            raise InvalidIRDException
        else:
            logger.info("Magic Verified")

        #: IRD file format version
        self.version: int = read_u8(f)
        logger.info(f"IRD Version: {self.version}")

        #: Game ID (ex. BLUS12354)
        self.game_id: str = f.read(GAME_ID_SIZE).decode('UTF-8')
        logger.info(f"Game ID: {self.game_id}")

        #: Game name length
        self.game_name_size: int = read_u8(f)
        #: Game name
        self.game_name: str = f.read(self.game_name_size).decode('UTF-8')
        logger.debug(f"Game Name Size: {self.game_name_size}")
        logger.info(f"Game Name: {self.game_name}")

        #: Update version
        self.update_version: str = f.read(4)
        #: Game version
        self.game_version: str = f.read(5)
        #: App version
        self.app_version: str = f.read(5)
        logger.info(f"Update Version: {self.update_version}")
        logger.info(f"Game Version: {self.game_version}")
        logger.info(f"App Version: {self.app_version}")
