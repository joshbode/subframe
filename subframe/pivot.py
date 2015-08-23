"""
Pivot table display.
"""

from .subframe import SubFrame
from .plugin import plugins


class PivotTable(SubFrame):
    """Display a DataFrame as a pivot table."""

    _plugins = [plugins.pivot, plugins.d3, plugins.c3]

    def __init__(self, data, labels=None, options=None):

        super(PivotTable, self).__init__(data, labels, options)

    def _js(self, data):
        """Javascript callback body."""

        data = data.to_records()
        data = self._json([self._map_columns(data.dtype.names)] + data.tolist())

        return "element.pivotUI({}, {});".format(data, self._json(self._options))
