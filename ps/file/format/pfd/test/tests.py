import logging
import os
import unittest

from ps.file.format.pfd import PFD

logging.basicConfig(level=logging.DEBUG, format='%(name)-32s: %(levelname)-8s %(message)s')

logger = logging.getLogger('PFD Test')


class Tests(unittest.TestCase):

    def test_parser_pfd(self):
        for root, dirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
            for file in files:
                if file.endswith('.PFD') or file.endswith('.pfd'):
                    file = os.path.join(root, file)
                    PFD(file)
                    return
