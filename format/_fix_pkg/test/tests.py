import logging
import os
import unittest

from format._fix_pkg import PKG

logging.basicConfig(level=logging.DEBUG, format='%(name)-32s: %(levelname)-8s %(message)s')


class PKGParsingTest(unittest.TestCase):

    def test_parser_pkg(self):
        for root, dirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
            for file in files:
                if file.endswith('.pkg') or file.endswith('.PKG'):
                    file = os.path.join(root, file)
                    PKG(file)
