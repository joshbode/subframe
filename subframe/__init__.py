"""
Subframe data display mappers.
"""

import notebook.nbextensions

from .datatables import DataTable
from .pivot import PivotTable
from .plugin import plugins
from .error import SubFrameError


__all__ = ['DataTable', 'PivotTable', 'SubFrameError']

# install static files
plugins.install(notebook.nbextensions.jupyter_data_dir())
