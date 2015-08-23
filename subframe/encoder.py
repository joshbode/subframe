"""
Custom JSON Encoder.
"""

import json
import json.encoder


class JS(str):
    """Javascript JSON Encoder Wrapper."""

    def __new__(cls, s):

        return super(JS, cls).__new__(cls, s)

    def __str__(self):

        return self

    def __repr__(self):

        return str(self)


# monkey-patch encode basestring to permit unquoted javascript representations
def encode_basestring_ascii(s):

    if isinstance(s, JS):
        return s
    else:
        return _original_encode_basestring_ascii(s)

_original_encode_basestring_ascii = json.encoder.encode_basestring_ascii
json.encoder.encode_basestring_ascii = encode_basestring_ascii
