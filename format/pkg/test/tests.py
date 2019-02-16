import logging
import os
import unittest

from base.errors import EmptyFileException
from format.pkg import PKG

logging.basicConfig(level=logging.DEBUG, format='%(name)-32s: %(levelname)-8s %(message)s')


# noinspection PyMethodMayBeStatic
class PKGParsingTest(unittest.TestCase):

    def test_parser_pkg(self):
        for root, dirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
            for file in files:
                if file.endswith('.pkg') or file.endswith('.PKG'):
                    file = os.path.join(root, file)
                    PKG(file)

    def test_pkg_library(self):
        for root, dirs, files in os.walk("H:\\PSNDL"):
            for file in files:
                if file.endswith('.pkg') or file.endswith('.PKG'):
                    file = os.path.join(root, file)
                    print(file)
                    try:
                        pkg: PKG = PKG(file)
                    except EmptyFileException:
                        logging.error(f'{file} is 0 bytes, something is wrong.')

    def test_update_library(self):
        for root, dirs, files in os.walk("H:\\PSN"):
            for file in files:
                if file.lower().endswith('.pkg'):
                    file = os.path.join(root, file)
                    print(file)
                    try:
                        pkg: PKG = PKG(file)
                    except EmptyFileException:
                        logging.error(f'{file} is 0 bytes, something is wrong.')
