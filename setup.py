#!/usr/bin/env python

import os
import os.path
import shutil
from glob import glob
from itertools import groupby
from operator import itemgetter

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.build_py import build_py


# files
static_files = [
    ('datatables', ['libs/DataTables/license.txt']),
    ('datatables/js', ['libs/DataTables/media/js/jquery.dataTables.min.js']),
    ('datatables/css', ['libs/DataTables/media/css/jquery.dataTables.min.css']),
    ('datatables/images', glob('libs/DataTables/media/images/*.png')),

    ('pivot', ['libs/pivottable/LICENSE.md']),
    ('pivot/js', ['libs/pivottable/dist/pivot.min.js'] + glob('libs/pivottable/dist/pivot.*.min.js') + glob('libs/pivottable/dist/*_renderers.min.js')),
    ('pivot/css', ['libs/pivottable/dist/pivot.min.css']),
    ('pivot/images', []),

    ('d3', ['libs/d3/LICENSE']),
    ('d3/js', ['libs/d3/d3.min.js']),
    ('d3/css', []),
    ('d3/images', []),

    ('c3', ['libs/c3/LICENSE']),
    ('c3/js', ['libs/c3/c3.min.js']),
    ('c3/css', ['libs/c3/c3.min.css']),
    ('c3/images', []),
]


def collate_files(root, files):
    """Collate static files."""

    root = os.path.join(os.path.split(__file__)[0], root)

    # remove existing directory
    try:
        os.rmdir(root)
    except OSError:
        pass

    for dir, group in groupby(sorted(files), key=itemgetter(0)):
        dir = os.path.join(root, dir)
        if not os.path.exists(dir):
            os.makedirs(dir)
        for _, filenames in group:
            for filename in filenames:
                shutil.copy(filename, dir)


class Develop(develop):
    """Custom develop command."""

    def run(self):
        """Copy static files."""

        collate_files('subframe/static', static_files)
        develop.run(self)


class BuildPy(build_py):
    """Custom build command."""

    def run(self):
        """Copy static files."""

        collate_files('subframe/static', static_files)
        build_py.run(self)


setup(
    name='subframe',
    version='0.0.1',
    description="Jupyter-Pandas DataFrame integration and visualisation",
    long_description=open('DESCRIPTION.rst', 'r').read(),
    url='https://github.com/joshbode/subframe',
    author="Josh Bode",
    author_email='joshbode@fastmail.com',
    license='MIT',
    classifiers=[],
    keywords=['ipython', 'notebook', 'dataframe'],
    packages=['subframe'],
    include_package_data=True,
    zip_safe=True,
    install_requires=['ipython', 'notebook', 'pandas'],
    cmdclass={
        'develop': Develop,
        'build_py': BuildPy
    }
)
