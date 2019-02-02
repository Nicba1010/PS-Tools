import logging

import click

from ps.pkg import Pkg, PkgEntry

logging.basicConfig(level=logging.DEBUG, format='%(name)-12s: %(levelname)-8s %(message)s')


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
@click.argument('file')
def extract(**kwargs):
    """
    Extract Sony Playstation 3 PKG file contents
    """
    file_path: str = kwargs["file"]
    pkg_file: Pkg = Pkg(file_path)
    file: PkgEntry
    for file in pkg_file.files:
        # TODO: Fix to use title_id but need to fix metadata for that
        file.save_file(f'{pkg_file.header.content_id}/', use_package_path=True)


if __name__ == '__main__':
    pstools()
