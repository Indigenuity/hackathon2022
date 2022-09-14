# import pytest
# import s3zero
# import unicodedata
#
# EXPECTED_CHARACTER_COUNT = 137743
#
# @pytest.fixture
# def safe_iter():
#     return s3zero.SafeUTF8Iterator(digits=1)
#
#
# @pytest.fixture
# def large_safe_iter():
#     return s3zero.SafeUTF8Iterator(digits=2)
#
#
# @pytest.fixture
# def unsafe_chars():
#     """This is only a sampling of the unsafe characters"""
#     return [
#         chr(0),         # null character
#         r"\\",          # backslash, illegal in JSON
#         "<",            # reserved in XML
#         ":",            # reserved in S3Zero
#         chr(0x08),      # backspace
#         chr(0x15),      # shift out
#         chr(0x80000),   # unnamed char (as of 01/2022)
#         chr(0xFFFFE),   # low surrogate
#         chr(0x10FFFF),  # high surrogate
#     ]
#
#
# @pytest.fixture
# def safe_chars():
#     """This is only a sampling of safe characters"""
#     return [
#         # "!",            # bang
#         # " ",            # space
#         # "蛙",            # frog
#         # "𓆏",            # frog
#     ]
#
#
# def test_is_safe(safe_chars, unsafe_chars):
#     for char in safe_chars:
#         assert s3zero.is_safe(char)
#     for char in unsafe_chars:
#         assert not s3zero.is_safe(char)
#
#
# def test_is_iterable(safe_iter):
#     for _ in safe_iter:
#         break
#
#
# def test_large_is_iterable(large_safe_iter):
#     for _ in large_safe_iter:
#         break
#
#
# def test_length(safe_iter):
#     count = 0
#     for _ in safe_iter:
#         count += 1
#     assert count == EXPECTED_CHARACTER_COUNT
#
#
# # This test would take too long, unfortunately
# # def test_large_length(large_safe_iter):
# #     count = 0
# #     for _ in large_safe_iter:
# #         count += 1
# #     assert count == EXPECTED_CHARACTER_COUNT ** 2
#
#
# def test_no_control_codes(safe_iter):
#     for char in safe_iter:
#         assert unicodedata.category(char)[0] != "C"
#
#
# def test_utf8_encodable(safe_iter):
#     for char in safe_iter:
#         char.encode("utf-8")
#
#
# def test_a_few_unsafe_chars(safe_iter):
#     unsafe_chars = ""
#     for char in safe_iter:
#         assert char not in unsafe_chars
#
