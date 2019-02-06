import logging
import os
import shutil
import subprocess
import unittest

from ps.file.format.psarc import PSARC
from ps.utils import file_md5

logging.basicConfig(level=logging.DEBUG, format='%(name)-32s: %(levelname)-8s %(message)s')

logger = logging.getLogger('PSARC Test')

script_path = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')


class Tests(unittest.TestCase):

    def test_parser_psarc(self):
        for root, dirs, files in os.walk(script_path):
            for file in files:
                if file.endswith(".psarc"):
                    #: Full File Path
                    file = os.path.join(root, file)

                    #: PSARC File Object
                    PSARC(file)

    def test_extraction_psarc(self):
        for root, dirs, files in os.walk(script_path):
            for file in files:
                if file.endswith(('.psarc', '.PSARC')):
                    #: Full File Path
                    file_path = os.path.join(root, file)

                    #: PSARC File Object
                    psarc_file: PSARC = PSARC(file_path)

                    #: Target Extraction Directory
                    target_dir: str = f'./{file}.dec/'

                    #: Target Reference Tool Extraction Directory
                    extraction_reference_dir = './extraction_test_reference/'

                    #: Created
                    for entry in psarc_file.entries[1:]:
                        psarc_file.save_entry(entry, target_dir)

                    #: Call Reference Tool
                    subprocess.call(
                        [os.path.join(script_path, './reference_tools/psarc.exe'),
                         'extract', file_path, '--to', extraction_reference_dir, '--overwrite']
                    )

                    #: Compare Reference Tool Hashes to the Output File Hashes
                    for root_, dirs_, files_ in os.walk(os.path.join(script_path, extraction_reference_dir)):
                        for file_ in files_:
                            #: Full File Path
                            file_path_ = os.path.join(root_, file_)

                            #: Full Reference Tool File Path
                            reference_tool_file_path = file_path_.replace(extraction_reference_dir, target_dir)

                            if not file_md5(file_path_) == file_md5(reference_tool_file_path):
                                self.fail(f'File hash for reference file does not match up with the file: {file_path_}')
                            else:
                                logger.info(f'File hashes for {file_path_} match up, extraction successful')

                    #: Remove Extracted Contents
                    shutil.rmtree(target_dir)

                    #: Remove Reference Tool Extracted Contents
                    shutil.rmtree(extraction_reference_dir)
