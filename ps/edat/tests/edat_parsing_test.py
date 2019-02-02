import logging
import unittest

from ps.edat.edat import EDAT

logging.basicConfig(level=logging.DEBUG, format='%(name)-24s: %(levelname)-8s %(message)s')


class IrdParsingTest(unittest.TestCase):

    def test_parser_sdat(self):
        try:
            EDAT('000b9d3233610e3b.sdat')
            EDAT('LVL_B005_CurvyFloor_3.edat')
        except Exception:
            self.fail(f'Test failed on file: {"000b9d3233610e3b.sdat"} or {"LVL_B005_CurvyFloor_3.edat"}')
