"""
Manage JavaScript plugins.
"""

import json
import os.path
import shutil
import re
from collections import OrderedDict

import pkg_resources
from IPython.display import display, Javascript
import ipywidgets

from .error import SubFrameError


def isiterable(x):
    """Determine if object is iterable."""

    # good enough, don't want to match strings
    return isinstance(x, (list, tuple))


class Plugin:
    """Plugin Loader."""

    _req = pkg_resources.Requirement.parse('subframe')
    _base = 'nbextensions'
    _cdn_re = re.compile(r'(https?:)?//')

    def __init__(self, name, main, js=None, css=None, images=None,
                 deps=None, init=None):

        self.name = name

        self.main = self._paths('js', [main])[0]

        # convert any single arguments into lists
        if js is not None and not isiterable(js):
            js = [js]
        if css is not None and not isiterable(css):
            css = [css]
        if images is not None and not isiterable(images):
            images = [images]
        if deps is not None and not isiterable(deps):
            deps = [deps]

        self.js = [x for x in self._paths('js', js) if x != self.main]
        self.css = self._paths('css', css)
        self.images = self._paths('images', images)

        self.init = init
        self.deps = deps if deps else []

    def install(self, root):
        """Install the plugin."""

        # copy resources to nbextensions
        for resource in [self.main] + self.js + self.css + self.images:
            if self._external(resource):
                continue

            dest = os.path.join(root, self._base, os.path.dirname(resource))
            if not os.path.exists(dest):
                os.makedirs(dest)

            # copy the file to the installation directory
            resource = pkg_resources.resource_filename(self._req, resource)
            shutil.copy(resource, dest)

    def _url(self, path):
        """Convert to url path."""

        if self._external(path):
            return path

        return '/' + os.path.join(self._base, path).replace(os.path.sep, '/')

    def enable(self):
        """Activate the plugin."""

        # load css
        if self.css:
            display(Javascript("$('head').append('{}');".format(' '.join(
                '<link rel="stylesheet" href="{}" />'.format(self._url(path))
                for path in self.css
            ))))

        # register JS requirements
        config_data = {
            'paths': {self.name: self._url(os.path.splitext(self.main)[0])},
            'shim': {self.name: {'deps': self.deps}},
        }

        # register ancillary supporting scripts/modules
        js = [self._url(path) for path in self.js]
        if self.js:
            config_data['shim'].update({
                path: {'deps': [self.name] + self.deps}
                for path in js
            })

        display(Javascript('require.config({});'.format(json.dumps(config_data))))

        # run initialisation (might be a hack?)
        if self.init or self.js:
            display(Javascript("require([{deps}], function({args}) {{ {init} }});".format(
                deps=', '.join("'{}'".format(dep) for dep in ([self.name] + self.deps + js)),
                args=', '.join(
                    [self.name] + [dep.split('/')[-1] for dep in self.deps]
                ),
                init=self.init if self.init else ''
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

        root = os.path.join('subframe/static', self.name, kind)

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

    def __init__(self, *plugins):
        """Iniitialise the plugin manager."""

        self._plugins = OrderedDict((plugin.name, plugin) for plugin in plugins)

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
    Plugin(
        'selectize', main='selectize.min.js',
        deps=['jquery', 'nbextensions/widgets/widgets/js/manager', 'nbextensions/widgets/widgets/js/widget_selection'],
        init="""\
var SelectizeView = widget_selection.SelectMultipleView.extend({
  render: function() {
    this.$el.addClass('widget-hbox widget-selectize');
    this.$label = $('<label />').appendTo(this.$el)
      .addClass('widget-label')
      .attr('for', 'input-selectize')
      .hide();
    this.$listbox = $('<select />').appendTo(this.$el)
      .addClass('widget-listbox')
      .attr('id', 'input-selectize').attr('multiple', true)
      .on('change', $.proxy(this.handle_change, this));
    this.update();
  },

  update: function(options) {
    SelectizeView.__super__.update.apply(this);
    this.$listbox.selectize({
      create: this.model.get('create'),
      createFilter: this.model.get('createFilter') || null,
      persist: this.model.get('persist'),
      maxItems: this.model.get('maxItems') || null
    });
  }
});
manager.WidgetManager.register_widget_view('SelectizeView', SelectizeView);"""
    ),
    Plugin('datatables', main='jquery.dataTables.min.js', deps=['jquery']),
    Plugin('d3', main='d3.min.js'),
    Plugin('c3', main='c3.min.js', deps=['d3']),
    Plugin(
        'pivot', main='pivot.min.js',
        js=['d3_renderers.min.js', 'c3_renderers.min.js', 'export_renderers.min.js'],
        deps=['jquery', 'jqueryui', 'd3', 'c3'],
        init="""\
$.pivotUtilities.renderers = $.extend(
  $.pivotUtilities.renderers,
  $.pivotUtilities.d3_renderers, $.pivotUtilities.c3_renderers, $.pivotUtilities.export_renderers
);"""  # monkey-patch all the renderers!
    ),
)
