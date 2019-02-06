import logging
import os
import unittest

from format.edat import EDAT

logging.basicConfig(level=logging.DEBUG, format='%(name)-32s: %(levelname)-8s %(message)s')


class IrdParsingTest(unittest.TestCase):

    # noinspection PyMethodMayBeStatic
    def test_parser_ird(self):
        for root, dirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
            for file in files:
                if file.endswith('.sdat') or file.endswith('.edat'):
                    file = os.path.join(root, file)
                    EDAT(file)
