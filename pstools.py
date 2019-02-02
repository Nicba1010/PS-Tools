import logging

import click

from ps.pkg import Pkg
from ps.sfo.sfo import SFO

logging.basicConfig(level=logging.DEBUG, format='%(name)-24s: %(levelname)-8s %(message)s')


@click.group('pkg')
def pstools():
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
    file_path: str = file
    SFO(file_path)


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


if __name__ == '__main__':
    pstools()
