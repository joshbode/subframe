"""
Manage JavaScript plugins.
"""

import json
import os.path
import shutil
import re

import pkg_resources
from IPython.display import display, Javascript, HTML

from .error import SubFrameError


class Plugin:
    """Plugin Loader."""

    _req = pkg_resources.Requirement.parse('subframe')
    _base = 'nbextensions/subframe'
    _cdn_re = re.compile(r'(https?:)?//')

    def __init__(self, name, js=None, css=None, images=None, deps=None, init=None):

        self.name = name

        # convert into lists any single arguments
        if isinstance(js, basestring):
            js = [js]
        if isinstance(css, basestring):
            css = [css]
        if isinstance(images, basestring):
            images = [images]
        if isinstance(deps, basestring):
            deps = [deps]

        self.js = self._paths('js', js)
        self.css = self._paths('css', css)
        self.images = self._paths('images', images)

        self.init = init
        self.deps = deps if deps else []

    def install(self, root):
        """Install the plugin."""

        # copy resources to nbextensions
        for resource in self.js + self.css + self.images:
            if self._external(resource):
                continue

            dest = os.path.join(root, self._base, os.path.dirname(resource))
            if not os.path.exists(dest):
                os.makedirs(dest)

            # copy the file to the installation directory
            resource = pkg_resources.resource_filename(self._req, resource)
            shutil.copy(resource, dest)

    def enable(self):
        """Activate the plugin."""

        # load css
        display(HTML('\n'.join(
            '<link rel="stylesheet" href="/{}" />'.format(
                path if self._external(path) else
                os.path.join(self._base, path).replace(os.path.sep, '/')
            )
            for path in self.css
        )))

        # register JS requirements
        config_data = json.dumps({
            'paths': {self.name: [
                os.path.splitext(
                    path if self._external(path) else
                    '/' + os.path.join(self._base, path).replace(os.path.sep, '/')
                )[0]
                for path in self.js
            ]},
            'shim': {self.name: self.deps},
        })
        display(Javascript('require.config({});'.format(config_data)))

        # run initialisation code for plugin if any
        if self.init:
            plugins = ', '.join("'{}'".format(plugin) for plugin in [self.name] + self.deps)
            display(Javascript("require([{plugins}], function() {{ {init} }});".format(
                plugins=plugins, init=self.init
            )))

    def _external(self, x):

        return bool(self._cdn_re.match(x))

    def _walk(self, root):
        """Walk resource structure."""

        for path in pkg_resources.resource_listdir(self._req, root):
            path = os.path.join(root, path)
            if pkg_resources.resource_isdir(self._req, path):
                for x in self._walk(path):
                    yield x
            else:
                yield path

    def _paths(self, kind, filter=None):
        """Get resource names."""

        root = os.path.join('static', self.name, kind)

        if filter is not None:
            # split into internal and external resources
            filter = [
                os.path.join(root, x) if not self._external(x) else x
                for x in filter
            ]
            internal = [x for x in filter if not self._external(x)]
            external = [x for x in filter if self._external(x)]

            # check if pure external
            if internal == ['*']:
                internal = []
            elif external and not internal:
                return external
        else:
            internal, external = [], []

        # walk any resources that exist
        if pkg_resources.resource_exists(self._req, root):
            result = list(self._walk(root))
        else:
            result = []

        if internal:
            result = [x for x in internal if x in result]
            missing = set(internal) - set(result)
            if missing:
                raise SubFrameError(
                    "Missing static {} resources from {}: {}".format(
                        kind, root, ','.join(sorted(missing))
                    )
                )
            return filter  # original order
        else:
            return result + external


class PluginManager(object):
    """Class to manage plugins."""

    def __init__(self, **plugins):
        """Iniitialise the plugin manager."""

        self._plugins = plugins

    def __getattr__(self, name):
        """Get attribute, try plugin name."""

        try:
            return self._plugins[name]
        except KeyError:
            return super(PluginManager, self).__getattribute__(name)

    def register(self, name, plugin):
        """Register a plugin."""

        self._plugins[name] = plugin

    def install(self, root):
        """Install managed plugins."""

        for plugin in self._plugins.values():
            plugin.install(root)

    def enable(self):
        """Enable managed plugins."""

        for plugin in self._plugins.values():
            plugin.enable()

    def __dir__(self):
        """Attribute directory."""

        return sorted(self._plugins.keys() + dir(type(self)))


# setup plugins under the manager
plugins = PluginManager(
    # google=Plugin('google', js='//www.google.com/jsapi', init="google.load('visualization', '1.0', {'packages': ['corechart', 'charteditor']});"),
    datatables=Plugin('datatables', js='jquery.dataTables.min.js', deps='jquery'),
    d3=Plugin('d3', js='d3.min.js'),
    pivot=Plugin('pivot', js='pivot.min.js', deps=['jquery', 'jqueryui']),
)
