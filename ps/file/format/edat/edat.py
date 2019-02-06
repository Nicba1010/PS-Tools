import logging
import os

from .errors import EmptyEDATException
from .header import EDATHeader

logger = logging.getLogger('EDAT')


class EDAT(object):
    def __init__(self, path: str):
        #: EDAT File Path
        self.path: str = path

        logger.info(f"Parsing file: {self.path}")

        if os.stat(self.path).st_size == 0:
            logger.error("Error, file is empty")
            raise EmptyEDATException()

        with open(self.path, 'rb') as f:
            #: EDAT file header
            self.header: EDATHeader = EDATHeader(f)
