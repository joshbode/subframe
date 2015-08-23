#!/usr/bin/env python

import os
import os.path
from itertools import groupby
from operator import itemgetter
import shutil
from glob import glob

from setuptools import setup
from setuptools.command.develop import develop

data_files = [
    ('static/datatables/js', ['libs/DataTables/media/js/jquery.dataTables.min.js']),
    ('static/datatables/css', ['libs/DataTables/media/css/jquery.dataTables.min.css']),
    ('static/datatables/images', glob('libs/DataTables/media/images/*.png')),
    ('static/pivot/js', ['libs/pivottable/dist/pivot.min.js'] + glob('libs/pivottable/dist/*_renderers.min.js')),
    ('static/pivot/css', ['libs/pivottable/dist/pivot.min.css']),
    ('static/pivot/images', []),
    ('static/d3/js', ['libs/d3/d3.min.js']),
    ('static/d3/css', []),
    ('static/d3/images', []),
    ('static/c3/js', ['libs/c3/c3.min.js']),
    ('static/c3/css', ['libs/c3/c3.min.css']),
    ('static/c3/images', []),
]


class Develop(develop):
    """Custom develop command."""

    def run(self):
        """Copy static files."""

        develop.run(self)
        root = os.path.split(__file__)[0]

        for dir, group in groupby(sorted(data_files), key=itemgetter(0)):
            dir = os.path.join(root, dir)
            if not os.path.exists(dir):
                os.makedirs(dir)
            for _, filenames in group:
                for filename in filenames:
                    shutil.copy(filename, dir)


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
    data_files=data_files,
    install_requires=['ipython', 'notebook', 'pandas'],
    cmdclass={
        'develop': Develop
    }
)
