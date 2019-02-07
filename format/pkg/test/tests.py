import logging
import os
import unittest

from format.pkg import PKG
from format.pkg.revision import PkgRevision

logging.basicConfig(level=logging.DEBUG, format='%(name)-32s: %(levelname)-8s %(message)s')


class PKGParsingTest(unittest.TestCase):

    # noinspection PyMethodMayBeStatic
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
                    pkg: PKG = PKG(file, verify_pkg_hash=False)
                    if pkg.header.revision == PkgRevision.DEBUG:
                        print(pkg.path)
                        return
