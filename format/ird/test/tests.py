import logging
import os
import unittest

from format.ird import IRD

logging.basicConfig(level=logging.DEBUG, format='%(name)-32s: %(levelname)-8s %(message)s')


class IrdParsingTest(unittest.TestCase):
    # CHANGE ME TO YOUR IRD DIRECTORY
    IRD_DIRECTORY = "H:/IRD"

    def test_parser(self):
        for root, dirs, files in os.walk(self.IRD_DIRECTORY):
            for file in files:
                if file.endswith(".ird"):
                    file = os.path.join(root, file)
                    # noinspection PyBroadException
                    try:
                        IRD(file)
                    except Exception:
                        self.fail(f'Test failed on file: {file}')
