from collections import OrderedDict
import re
import sys
import unicodedata


invalid_xml_unicode_ranges = [(0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F), (0x7F, 0x84), (0x86, 0x9F), (0xFDD0, 0xFDDF),
                              (0xFFFE, 0xFFFF)]
discouraged_xml_unicode_ranges = [(0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), (0x3FFFE, 0x3FFFF), (0x4FFFE, 0x4FFFF),
                                  (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF), (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF),
                                  (0x9FFFE, 0x9FFFF), (0xAFFFE, 0xAFFFF), (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
                                  (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), (0xFFFFE, 0xFFFFF), (0x10FFFE, 0x10FFFF)]
unsafe_unicode_ranges = invalid_xml_unicode_ranges + discouraged_xml_unicode_ranges
unsafe_char_ranges = [fr"{chr(low)}-{chr(high)}" for (low, high) in unsafe_unicode_ranges]

null_char = chr(0)
json_special_chars = r"\"\\"             # This is: " \
xml_predefined_entity_chars = r"\"<>'&"  # This is: " < > ' &
s3_zero_reserved_chars = ":/"
generally_annoying_chars = r"\.\^\$\*\+\-\?\(\)\[\]\{\}\|%`~"

unsafe_chars = null_char + json_special_chars + xml_predefined_entity_chars + s3_zero_reserved_chars + \
               generally_annoying_chars

unsafe_regex = re.compile(f"[{unsafe_chars}{''.join(unsafe_char_ranges)}]")

safe_chars = OrderedDict()
for b in range(sys.maxunicode):
    s = chr(b)
    if unsafe_regex.search(s):
        continue

    # Does it fail to encode to utf8?
    try:
        s.encode("utf-8")
    except UnicodeEncodeError:
        continue

    # Does it contain a control code?  Is it unassigned? The "Cn" category is unassigned
    if unicodedata.category(s)[0] == "C":
        continue

    # Is it just whitespace?
    if s.isspace():
        continue

    safe_chars[s] = True

# A few checks
expected_char_count = 137724
expected_unicode_version = "12.1.0"
actual_char_count = len(safe_chars.keys())
actual_version = unicodedata.unidata_version
if actual_char_count != expected_char_count:
    raise ValueError(f"Somehow ended up with wrong number of characters.  Expected {expected_char_count}, got {actual_char_count}")
if actual_version != expected_unicode_version:
    raise ValueError(f"Wrong Unicode version!  Expected {expected_unicode_version}, got {actual_version}")

target_file = "s3zero/data/safe_utf8.txt"
with open(target_file, 'w', encoding="utf-8") as f:
    for char in safe_chars.keys():
        f.write(char)

print(f"Wrote {actual_char_count} characters from unicode version {actual_version} to file {target_file}")