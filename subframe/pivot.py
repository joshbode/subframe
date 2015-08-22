"""
Pivot table display.
"""

from .subframe import SubFrame
from .plugin import plugins


class PivotTable(SubFrame):
    """Display a DataFrame as a pivot table."""

    _plugins = [plugins.pivot]

    def _js(self, data):
        """Javascript callback body."""

        data = data.to_records()
        data = self._json([self._map_columns(data.dtype.names)] + data.tolist())

        return "element.pivotUI({});".format(data)
