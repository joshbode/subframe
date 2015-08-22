"""
DataTable display.
"""

from .subframe import SubFrame
from .plugin import plugins


class DataTable(SubFrame):
    """Display a DataFrame as a DataTable."""

    _plugins = [plugins.datatables]

    def _js(self, data):
        """Javascript callback body."""

        data = data.to_records()
        data = self._json({
            'data': data.tolist(),
            'columns': [
                {'title:': x} for x in self._map_columns(data.dtype.names)
            ]
        })

        return "element.append('<table />').find('table').DataTable({});".format(data)
