"""
Custom widgets.
"""

from ipywidgets import SelectMultiple
from traitlets import Unicode, Bool, Int


class Selectize(SelectMultiple):
    """Selectize Widget"""

    _view_name = Unicode('SelectizeView', sync=True)

    create = Bool(False, help="Allow user to create new items", sync=True)
    createFilter = Unicode('', help="Regular expression that the created items must match", sync=True)
    persist = Bool(False, help="Persist created items after they are deselected", sync=True)
    maxItems = Int(0, help="Max number of items user can select", sync=True)

    allowEmpty = Bool(True, help="Allow no selection", sync=True)

    def _value_in_options(self):
        """Ensure value is in options."""

        # allow empty value
        if self.value or not self.allowEmpty:
            super(Selectize, self)._value_in_options()
