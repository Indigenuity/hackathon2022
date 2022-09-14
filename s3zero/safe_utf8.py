"""
The necessary constants, helpers, and classes necessary for iterating through "safe" utf8 characters.

The high-level idea of an "unsafe" character is defined by the parent module as unicode code points that are:
    - the NULL code (0x00)
    - not encodable to utf8
    - control codes
    - reserved by the `myapp` parent module
    - illegal in XML
    - discouraged in XML
    - a predefined entity in XML
    - illegal in JSON strings
    - whitespace
"""
import itertools
from itertools import islice

import os
import sys
import unicodedata
from collections import OrderedDict


# Should maybe lazy-load the safe chars, but I'm too lazy
module_dir = os.path.dirname(sys.modules["s3zero"].__file__)
safe_chars_file = os.path.join(module_dir, "data/safe_utf8.txt")
safe_chars_map = OrderedDict()
for char in open(safe_chars_file, 'r', encoding="utf-8").read():
    safe_chars_map[char] = True
max_char_index = len(safe_chars_map) - 1


def is_safe(s: str):
    if not isinstance(s, str):
        raise ValueError("Expected value of type 'str'")
    # if len(s) != 1:
    #     raise ValueError("This function can only validate strings of length 1")
    return safe_chars_map.get(s, False)


class SafeUTF8Iterator:
    """
    Iterate over all utf8-encodable unicode points in lexical order, skipping "unsafe" ones
    """
    def __init__(self, digits=2):
        self.digits = digits
        self.safe_chars = safe_chars_map.keys()
        self.iterable = itertools.product(iter(safe_chars_map.keys()), repeat=self.digits)

    def __iter__(self):
        return self

    def __next__(self):
        return str.join("", next(self.iterable))

    def next(self):
        return self.__next__()

    def keyspace_size(self):
        return len(self.safe_chars) ** self.digits
