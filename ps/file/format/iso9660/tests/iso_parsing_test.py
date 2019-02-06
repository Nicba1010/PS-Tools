import logging
import os
import unittest

from ps.file.format.iso9660 import ISO9660

logging.basicConfig(level=logging.DEBUG, format='%(name)-32s: %(levelname)-8s %(message)s')


class ISOParsingTest(unittest.TestCase):
    # CHANGE ME TO YOUR ISO DIRECTORY
    ISO_DIRECTORY = "H:\\ISO\\PS3"

    def test_parser(self):
        for root, dirs, files in os.walk(self.ISO_DIRECTORY):
            for file in files:
                if file.endswith(".iso"):
                    file = os.path.join(root, file)
                    # noinspection PyBroadException
                    try:
                        ISO9660(file)
                    except Exception:
                        self.fail(f'Test failed on file: {file}')
