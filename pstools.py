import logging
import os

import click

from ps.pkg import Pkg
from ps.psarc import PSARC
from ps.sfo import SFO


@click.group()
@click.option('-v', '--verbose', count=True)
def pstools(verbose: int):
    if verbose == 1:
        logging.basicConfig(level=logging.DEBUG, format='%(name)-24s: %(levelname)-8s %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(name)-24s: %(levelname)-8s %(message)s')
    """
    A comprehensive set of tools related to the Sony Playstation console files
    """
    pass


@pstools.group()
def pkg():
    """
    A set of tools to be used with the Sony Playstation 3 PKG file format
    """
    pass


@pkg.command()
@click.argument('file', type=str)
@click.option('--verify/--no-verify', default=True)
def info(file: str, verify: bool):
    """
    Info about Sony Playstation 3 PKG file contents
    """
    Pkg(file, verify_pkg_hash=verify)


@pkg.command()
@click.argument('file', type=str)
@click.option('--verify/--no-verify', default=True)
def extract(file: str, verify: bool):
    """
    Extract Sony Playstation 3 PKG file contents
    """
    pkg_file: Pkg = Pkg(file, verify_pkg_hash=verify)
    for entry in pkg_file.files:
        # TODO: Fix to use title_id but need to fix metadata for that
        entry.save_file(f'{pkg_file.header.content_id}/', use_package_path=True)


@pstools.group()
def sfo():
    """
    A set of tools to be used with the Sony Playstation SFO file format
    """
    pass


@sfo.command()
@click.argument('file')
def info(file: str):
    """
    Info about Sony Playstation SFO file contents
    """
    SFO(file)


@sfo.command()
@click.argument('file', type=str)
@click.option('--out-file', '-o', default=None, type=str)
def edit(file: str, out_file: str):
    """
    Edit Sony Playstation SFO file contents
    """
    sfo_file: SFO = SFO(file)
    while True:
        #: Adding NULL Terminator because the keys contain the NULL Terminator in the file already
        key: str = input('Enter key of the entry you would like to edit (q -> quit, w -> write and quit): ') + '\0'
        if key == 'q\0':
            return
        elif key == 'w\0':
            sfo_file.write(out_file)
            return
        data: str = input('Enter entry data: ')
        sfo_file.set_data(key, data)
        sfo_file.print_key_data_map()


@pstools.group()
def psarc():
    """
    A set of tools to be used with the Sony Playstation Archive (PSARC) file format
    """
    pass


@psarc.command()
@click.argument('file')
def info(file: str):
    """
    Info about Sony Playstation Archive (PSARC) file contents
    """
    PSARC(file)


# noinspection PyShadowingBuiltins
@psarc.command()
@click.argument('file', type=str)
@click.option('--dir', default=None, type=str, help='target directory for extraction (default = archive name)')
@click.option('--use-package-path/--no-use-package-path', default=True, help='extract with directory structure')
@click.option('--create-directories/--no-create-directories', default=True, help='create needed directory structure')
@click.option('--overwrite/--no-overwrite', default=True, help='overwrite already extracted files')
def extract(file: str, dir: str, use_package_path: bool, create_directories: bool, overwrite: bool):
    """
    Extract Sony Playstation Archive (PSARC) file contents
    """
    psarc_file: PSARC = PSARC(file)
    if dir is None:
        dir = f'./{os.path.basename(file)}/'
    for entry in psarc_file.entries[1:]:
        psarc_file.save_entry(
            entry, dir, use_package_path=use_package_path, create_directories=create_directories, overwrite=overwrite
        )


if __name__ == '__main__':
    pstools()
