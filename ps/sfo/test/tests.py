import logging
import os
import unittest

from ps.sfo.sfo import SFO
from ps.utils import file_md5

logging.basicConfig(level=logging.DEBUG, format='%(name)-24s: %(levelname)-8s %(message)s')

logger = logging.getLogger('SFO Test')


class Tests(unittest.TestCase):

    def test_parser_sdat(self):
        for root, dirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
            for file in files:
                if file.endswith(".SFO"):
                    file = os.path.join(root, file)
                    SFO(file)

    def test_writing_sdat(self):
        for root, dirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
            for file in files:
                if file.endswith(".SFO"):
                    file = os.path.join(root, file)
                    verification_file = f'{file}.VERIFY'
                    SFO(file).write(verification_file)
                    if not file_md5(file) == file_md5(verification_file):
                        self.fail(f'File hash for reconstructed {file} does not match up with the original')
                    else:
                        logger.info(f'File hashes match up, reconstruction successful')
                    os.remove(verification_file)
