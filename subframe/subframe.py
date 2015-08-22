"""
Base class.
"""

import json

from IPython.display import Javascript


class SubFrame(Javascript):
    """Base Class."""

    _plugins = []

    def __init__(self, data, columns=None, opts=None):
        """Initialise SubFrame."""

        self._columns = columns if columns else {}
        plugins = ', '.join("'{}'".format(plugin.name) for plugin in self._plugins)
        data = "require([{plugins}], function() {{ {js} }});".format(
            plugins=plugins, js=self._js(data)
        )
        super(SubFrame, self).__init__(data)

    def _map_columns(self, columns):
        """Map column labels."""

        if not self._columns:
            return columns

        return [self._columns.get(x, x) for x in columns]

    def _js(self, data):
        """Javascript callback body."""

        raise NotImplementedError

    def _json(self, data):
        """JSON representation of data."""

        return json.dumps(data, separators=(',', ':'))
