import os
from typing import List

from base.file_format import FileFormatWithMagic
from utils.utils import human_size
from .header import PSARCHeader
from .toc import TOCEntry


class PSARC(FileFormatWithMagic[PSARCHeader]):
    def __init__(self, path: str):
        super().__init__(path, PSARCHeader)

        #: Read PSARC TOC Entries
        self.entries: List[TOCEntry] = list()
        for i in range(0, self.header.toc_entry_count):
            self.logger.debug(f'Reading TOC Entry #{i}')
            entry: TOCEntry = TOCEntry(self.file_handle)
            self.entries.append(entry)

        for i, entry in enumerate(self.entries):
            #: First entry contains file names
            if i == 0:
                #: Decompressed data read all at once into memory
                data: str = entry.read_entry_data(
                    self.file_handle, self.header.block_size, self.header.compression_type
                ).decode('UTF-8')

                for index, name in enumerate(data.splitlines(), start=1):
                    #: Set TOC Entry Name
                    actual_entry = self.entries[index]
                    actual_entry.name = name
                    self.logger.info(
                        f'Entry #{index} ({human_size(actual_entry.decompressed_size)}): {actual_entry.name}'
                    )

    def save_entry(self, entry: TOCEntry, path: str, use_package_path: bool = True, create_directories: bool = True,
                   overwrite: bool = True) -> bool:
        if (os.path.exists(path) and os.path.isdir(path)) or (
                not os.path.exists(path) and path.endswith(('/', '\\'))):
            if use_package_path:
                path = os.path.join(path, entry.name[1:] if entry.name.startswith(('/', '\\')) else entry.name)
            else:
                path = os.path.join(path, os.path.basename(entry.name))
        elif os.path.isfile(path):
            pass
        directory: str = os.path.dirname(path)
        # TODO: Do we really need this? Maybe for logging?
        # file_name: str = os.path.basename(path)

        if create_directories and not os.path.exists(directory):
            os.makedirs(directory)

            self.logger.info(f'Extracting entry: {entry.name} -> {path}')
        if not os.path.exists(path) or overwrite:
            # TODO: Do this in C so its somewhat performant at least
            with open(path, 'wb') as export:
                for data in entry.get_decompression_stream(
                        self.file_handle, self.header.block_size, self.header.compression_type
                ):
                    export.write(data)
                    self.logger.info(f'File extracted!')
                return True
        else:
            self.logger.info(
                'Could not extract file because a file with the same name already exists, turn on overwrite'
            )
            return False

    def __del__(self):
        self.logger.debug('Cleaning up...')
        if not self.file_handle.closed:
            self.file_handle.close()
