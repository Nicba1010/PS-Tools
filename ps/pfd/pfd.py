import logging
import os
from io import BytesIO

from .errors import EmptyPFDException
from .header import PFDHeader

logger = logging.getLogger('PFD')


class PFD(object):
    def __init__(self, path: str):
        #: File Path
        self.path: str = path

        logger.info(f"Parsing file: {self.path}")

        if os.stat(self.path).st_size == 0:
            logger.error("Error, file is empty")
            raise EmptyPFDException()

        self.file_handle: BytesIO = open(self.path, 'rb')

        #: File Header
        self.header: PFDHeader = PFDHeader(self.file_handle)

    def __del__(self):
        logger.info('Cleaning up...')
        if not self.file_handle.closed:
            self.file_handle.close()
