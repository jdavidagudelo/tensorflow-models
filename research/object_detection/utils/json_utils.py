# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Utilities for dealing with writing json strings.

json_utils wraps json.dump and json.dumps so that they can be used to safely
control the precision of floats when writing to json strings or files.
"""
import json
from json.encoder import _make_iterencode, py_encode_basestring_ascii, py_encode_basestring

try:
    from _json import encode_basestring_ascii as c_encode_basestring_ascii
except ImportError:
    c_encode_basestring_ascii = None
try:
    from _json import encode_basestring as c_encode_basestring
except ImportError:
    c_encode_basestring = None

try:
    from _json import make_encoder as c_make_encoder
except ImportError:
    c_make_encoder = None

encode_basestring_ascii = (
        c_encode_basestring_ascii or py_encode_basestring_ascii)
encode_basestring = (c_encode_basestring or py_encode_basestring)
INFINITY = float('inf')


class DecimalEncoder(json.JSONEncoder):
    def __init__(self, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False,
                 indent=None, separators=None, default=None, float_digits=2):
        super().__init__(skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                         allow_nan=allow_nan, sort_keys=sort_keys, indent=indent, separators=separators,
                         default=default)
        self.float_digits = float_digits

    def encode(self, o):
        if isinstance(o, float):
            if self.float_digits >= 0:
                return format(o, '.%df' % self.float_digits)
            else:
                return '{0}'.format(o)
        return super().encode(o)

    def iterencode(self, o, _one_shot=False):
        if self.check_circular:
            markers = {}
        else:
            markers = None
        if self.ensure_ascii:
            _encoder = encode_basestring_ascii
        else:
            _encoder = encode_basestring

        def floatstr(o, allow_nan=self.allow_nan,
                     _repr=float.__repr__, _inf=INFINITY, _neginf=-INFINITY):
            # Check for specials.  Note that this type of test is processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.

            if o != o:
                text = 'NaN'
            elif o == _inf:
                text = 'Infinity'
            elif o == _neginf:
                text = '-Infinity'
            else:
                if self.float_digits >= 0:
                    return format(o, '.%df' % self.float_digits)
                else:
                    return '{0}'.format(o)

            if not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " +
                    repr(o))

            return text

        if (_one_shot and c_make_encoder is not None
                and self.indent is None):
            _iterencode = c_make_encoder(
                markers, self.default, _encoder, self.indent,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, self.allow_nan)
        else:
            _iterencode = _make_iterencode(
                markers, self.default, _encoder, self.indent, floatstr,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, _one_shot)
        return _iterencode(o, 0)


def Dump(obj, fid, float_digits=-1, **params):
    """Wrapper of json.dump that allows specifying the float precision used.

  Args:
    obj: The object to dump.
    fid: The file id to write to.
    float_digits: The number of digits of precision when writing floats out.
    **params: Additional parameters to pass to json.dumps.
  """
    params['float_digits'] = float_digits
    json.dump(obj, fid, cls=DecimalEncoder, **params)


def Dumps(obj, float_digits=-1, **params):
    """Wrapper of json.dumps that allows specifying the float precision used.

  Args:
    obj: The object to dump.
    float_digits: The number of digits of precision when writing floats out.
    **params: Additional parameters to pass to json.dumps.

  Returns:
    output: JSON string representation of obj.
  """

    params['float_digits'] = float_digits
    output = json.dumps(obj, cls=DecimalEncoder, **params)
    return output


def PrettyParams(**params):
    """Returns parameters for use with Dump and Dumps to output pretty json.

  Example usage:
    ```json_str = json_utils.Dumps(obj, **json_utils.PrettyParams())```
    ```json_str = json_utils.Dumps(
                      obj, **json_utils.PrettyParams(allow_nans=False))```

  Args:
    **params: Additional params to pass to json.dump or json.dumps.

  Returns:
    params: Parameters that are compatible with json_utils.Dump and
      json_utils.Dumps.
  """
    params['float_digits'] = 4
    params['sort_keys'] = True
    params['indent'] = 2
    params['separators'] = (',', ': ')
    return params
