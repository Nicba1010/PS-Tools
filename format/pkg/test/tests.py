import logging
import os
import unittest

from base.errors import EmptyFileException
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

    # H:\PSN\NPEB02225\Retail\EP4173 - NPEB02225_00 - PARANORMAL000000 - A0101 - V0103 - PE.pkg
    def test_pkg_library(self):
        t = True
        for root, dirs, files in os.walk("H:\\PSNDL"):
            for file in files:
                if file.endswith('.pkg') or file.endswith('.PKG'):
                    file = os.path.join(root, file)
                    print(file)
                    if (
                            t and file != 'H:\PSNDL\EP0002-BLES01857_00-DSTCOMPATPACK003_bg_1_ca94211a55f7072ece887e194882baf68e2937a8.pkg') or file.endswith(
                        tuple(list([f'0{x}.pkg' for x in range(10)]))):
                        continue
                    t = False
                    pkg: PKG = PKG(file)
                    if pkg.header.revision == PkgRevision.DEBUG:
                        print(pkg.path)
                        return

    def test_update_library(self):
        t = True
        for root, dirs, files in os.walk("H:\\PSN"):
            for file in files:
                if file.lower().endswith('.pkg'):
                    file = os.path.join(root, file)
                    print(file)
                    if t and file != "H:\\PSN\\NPJB00453\\Debug\\JP0082-NPJB00453_00-FFXIVARR00000100-A0200-V0100.pkg":
                        continue
                    t = False
                    try:
                        pkg: PKG = PKG(file)
                    except EmptyFileException:
                        logging.error(f'{file} is 0 bytes, something is wrong.')
