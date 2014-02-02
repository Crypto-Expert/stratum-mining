# /usr/bin/env python
# coding=utf-8

#  Copyright 2010 Jonathan Bowman
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
#  implied. See the License for the specific language governing
#  permissions and limitations under the License.

"""Various helper functions for handling arrays, etc. using numpy"""

import struct
from operator import xor, add as add64, sub as sub64
import numpy as np

words = np.uint64
bytelist = np.uint8
bigint = np.uint64

# working out some differences between Python 2 and 3
try:
    from itertools import imap, izip
except ImportError:
    imap = map
    izip = zip
try:
    xrange = xrange
except:
    xrange = range

SKEIN_KS_PARITY = np.uint64(0x1BD11BDAA9FC1A22)

# zeroed out byte string and list for convenience and performance
zero_bytes = struct.pack('64B', *[0] * 64)
zero_words = np.zeros(8, dtype=np.uint64)

# Build structs for conversion appropriate to this system, favoring
# native formats if possible for slight performance benefit
words_format_tpl = "%dQ"
if struct.pack('2B', 0, 1) == struct.pack('=H', 1): # big endian?
    words_format_tpl = "<" + words_format_tpl # force little endian
else:
    try: # is 64-bit integer native?
        struct.unpack(words_format_tpl % 2, zero_bytes[:16])
    except(struct.error): # Use standard instead of native
        words_format_tpl = "=" + words_format_tpl

# build structs for one-, two- and eight-word sequences
words_format = dict(
    (i,struct.Struct(words_format_tpl % i)) for i in (1,2,8))

def bytes2words(data, length=8):
    """Return a list of `length` 64-bit words from `data`.

    `data` must consist of `length` * 8 bytes.
    `length` must be 1, 2, or 8.

    """
    return(np.fromstring(data, dtype=np.uint64))

def words2bytes(data, length=8):
    """Return a `length` * 8 byte string from `data`.


    `data` must be a list of `length` 64-bit words
    `length` must be 1, 2, or 8.

    """
    try:
        return(data.tostring())
    except AttributeError:
        return(np.uint64(data).tostring())

def RotL_64(x, N):
    """Return `x` rotated left by `N`."""
    #return (x << np.uint64(N & 63)) | (x >> np.uint64((64-N) & 63))
    return(np.left_shift(x, (N & 63), dtype=np.uint64) |
           np.right_shift(x, ((64-N) & 63), dtype=np.uint64))

def RotR_64(x, N):
    """Return `x` rotated right by `N`."""
    return(np.right_shift(x, (N & 63), dtype=np.uint64) |
           np.left_shift(x, ((64-N) & 63), dtype=np.uint64))

def add64(a,b):
    """Return a 64-bit integer sum of `a` and `b`."""
    return(np.add(a, b, dtype=np.uint64))

def sub64(a,b):
    """Return a 64-bit integer difference of `a` and `b`."""
    return(np.subtract(a, b, dtype=np.uint64))

