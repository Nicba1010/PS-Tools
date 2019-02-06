from typing import IO

from base.header import MagicFileHeader
from utils.utils import read_u8

GAME_ID_SIZE = 0x09


class IRDHeader(MagicFileHeader):

    def __init__(self, f: IO):
        super().__init__(f)

        #: IRD file format version
        self.version: int = read_u8(f)
        self.logger.info(f"IRD Version: {self.version}")

        #: Game ID (ex. BLUS12354)
        self.game_id: str = f.read(GAME_ID_SIZE).decode('UTF-8')
        self.logger.info(f"Game ID: {self.game_id}")

        #: Game name length
        self.game_name_size: int = read_u8(f)
        self.logger.debug(f"Game Name Size: {self.game_name_size}")

        #: Game name
        self.game_name: str = f.read(self.game_name_size).decode('UTF-8')
        self.logger.info(f"Game Name: {self.game_name}")

        #: Update version
        self.update_version: str = f.read(4)
        self.logger.info(f"Update Version: {self.update_version}")

        #: Game version
        self.game_version: str = f.read(5)
        self.logger.info(f"Game Version: {self.game_version}")

        #: App version
        self.app_version: str = f.read(5)
        self.logger.info(f"App Version: {self.app_version}")

    @property
    def magic(self) -> bytes:
        return b'3IRD'
