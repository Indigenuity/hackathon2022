# Figured I'd add some of the random scratchpad benchmarking I did while working on the project


import itertools
import os
import pkgutil
import re
import sys
import time
from collections import OrderedDict

start_time = time.time()
import s3zero
import random
print("--- IMPORT MODULE:  %s seconds ---" % (time.time() - start_time))

start_time = time.time()
test_nums = [random.randint(0, sys.maxunicode) for _ in range(1000000)]
test_strs = [chr(x) for x in test_nums]
print("--- GENERATE TEST VALUES:  %s seconds ---" % (time.time() - start_time))

start_time = time.time()
for char in test_strs:
    s3zero.is_safe(char)
print("--- IS_SAFE:  %s seconds ---" % (time.time() - start_time))

start_time = time.time()
digits = 2
# safe_char_iters = [s3zero.safe_chars_map.keys()] * digits
product = itertools.product(iter(s3zero.safe_chars_map.keys()), repeat=digits)
print(f"Size of safe_chars : {sys.getsizeof(s3zero.safe_chars_map)}")
print(f"Size of product : {sys.getsizeof(product)}")
print("--- GENERATE PRODUCT:  %s seconds ---" % (time.time() - start_time))

start_time = time.time()
count = 0
# for x in product:
for x in range(173000000):
    count += 1
    if count % 1000000 == 0:
        print(count)
print(f"count = {count}")
print(f"safesize = {len(s3zero.safe_chars_map)}")
print("--- ITERATE:  %s seconds ---" % (time.time() - start_time))

# REGEX_SPECIAL_CHARS = ".^$*+-?()[]{}\\|"
#
# valids = []
#
#
# start_time = time.time()
# for char in s3zero.SafeUTF8Iterator():
#     if char in REGEX_SPECIAL_CHARS:
#         valids.append(rf"\{char}")
#         print(f"balls, still getting specials: {char}")
#     else:
#         valids.append(char)
# print("--- GENERATE VALIDS:  %s seconds ---" % (time.time() - start_time))
#
# print(valids[:65])
# start_time = time.time()
# safe_regex = re.compile(rf"[{''.join(valids)}]")
# print("--- COMPILE VALIDS:  %s seconds ---" % (time.time() - start_time))

# count = 0
# start_time = time.time()
# for i in range(1, sys.maxunicode):
#     char = chr(i)
#     count += 1
#     if count %1000 == 0:
#         print(count)
#     if s3zero.is_safe(char) == (safe_regex.search(char) is None):
#         print(s3zero.is_safe(char))
#         print(safe_regex.search(char))
#         print(i)
#         raise Exception("balls")
# print("--- ASSUMPTION CHECKING:  %s seconds ---" % (time.time() - start_time))

# safes = OrderedDict()
# start_time = time.time()
# for char in valids:
#     safes[char] = True
# print("--- COMPILE SAFES:  %s seconds ---" % (time.time() - start_time))



# start_time = time.time()
# for char in test_strs:
#     safes.get(char)
# print("--- SAFES.GET:  %s seconds ---" % (time.time() - start_time))

# start_time = time.time()
# for char in test_strs:
#     safe_regex.search(char)
# print("--- SEARCH:  %s seconds ---" % (time.time() - start_time))

# start_time = time.time()
# for char in test_strs:
#     char in valids
# print("--- CHAR IN:  %s seconds ---" % (time.time() - start_time))

# start_time = time.time()
# with open(safes_file, 'w', encoding="utf-8") as f:
#     for item in valids:
#         f.write(item)
# print("--- WRITE VALIDS:  %s seconds ---" % (time.time() - start_time))



# start_time = time.time()
# loads = OrderedDict()
# stread = open(safes_file, 'r', encoding="utf-8").read()
# for char in stread:
#     loads[char] = True
# print(f"Length of loads: {len(loads)}")
# print(f"Length of valids: {len(valids)}")
# print(f"Length of safes: {len(valids)}")
# print("--- STR READ:  %s seconds ---" % (time.time() - start_time))

# start_time = time.time()
# for char in test_strs:
#     loads.get(char)
# print("--- LOADS.GET:  %s seconds ---" % (time.time() - start_time))
#
# print(f"size of valids : {sys.getsizeof(valids)}")
# print(f"size of safes : {sys.getsizeof(safes)}")
# print(f"size of loads : {sys.getsizeof(loads)}")
#
# print(loads == safes)
# print(list(loads.items()) == list(safes.items()))