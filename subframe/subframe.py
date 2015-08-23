"""
Base class.
"""

import json

from IPython.display import Javascript


class SubFrame(Javascript):
    """Base Class."""

    _plugins = []

    def __init__(self, data, labels=None, options=None):
        """Initialise SubFrame."""

        self._labels = labels if labels else {}
        self._options = options if options else {}
        data = "require([{plugins}], function({args}) {{ {js} }});".format(
            plugins=', '.join("'{}'".format(plugin.name) for plugin in self._plugins),
            args=', '.join(plugin.name for plugin in self._plugins),
            js=self._js(data)
        )
        super(SubFrame, self).__init__(data)

    def _map_columns(self, columns):
        """Map column labels."""

        if not self._labels:
            return columns

        return [self._labels.get(x, x) for x in columns]

    def _js(self, data):
        """Javascript callback body."""

        raise NotImplementedError

    def _json(self, data):
        """JSON representation of data."""

        return json.dumps(data, separators=(',', ':'))
