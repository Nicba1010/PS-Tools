import logging
import os
import unittest

import yaml

from base.errors import EmptyFileException
from format.pkg import PKG

logging.basicConfig(level=logging.DEBUG, format='%(name)-32s: %(levelname)-8s %(message)s')


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class PKGParsingTest(unittest.TestCase):

    def test_parser_pkg(self):
        for root, dirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
            for file in files:
                if file.endswith('.pkg') or file.endswith('.PKG'):
                    file = os.path.join(root, file)
                    print(file)
                    pkg: PKG = PKG(file)
                    with open('test.yaml', 'w') as f:
                        yaml.dump(pkg.files, f)
                    del pkg

    def test_pkg_library(self):
        cont = False
        for root, dirs, files in os.walk("H:\\PSNDL"):
            for file in files:
                if file.endswith('.pkg') or file.endswith('.PKG'):
                    file = os.path.join(root, file)
                    print(file)
                    if 'ySvU6Lui7Oq2wdOBeBonihi3ELX3XxUe8SFJe52jp8YhR6lfih45Aq6IjuFgkDXsoFabnI6YwCQRpgdCHIEltuWs4A5kVkmKn1yKs.pkg' in file:
                        cont = False
                    if cont or file[-6:] in [f'0{x}.pkg' for x in range(10)]:
                        continue
                    try:
                        pkg: PKG = PKG(file, verify=False)
                        del pkg
                    except EmptyFileException:
                        logging.error(f'{file} is 0 bytes, something is wrong.')

    def test_update_library(self):
        cont = True
        for root, dirs, files in os.walk("H:\\PSN"):
            for file in files:
                if file.lower().endswith('.pkg'):
                    file = os.path.join(root, file)
                    print(file)
                    if 'HP9000-NPHG00024_00-LOCOROCOMCPTCH01-A0200-V0101-PE.pkg' in file:
                        cont = False
                    if cont or file[-6:] in [f'0{x}.pkg' for x in range(10)]:
                        continue
                    try:
                        pkg: PKG = PKG(file, verify=False)
                        del pkg
                    except EmptyFileException:
                        logging.error(f'{file} is 0 bytes, something is wrong.')
