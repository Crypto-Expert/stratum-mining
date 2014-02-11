'''Various helper methods. It probably needs some cleanup.'''

import struct
import StringIO
import binascii

def deser_string(f):
    nit = struct.unpack("<B", f.read(1))[0]
    if nit == 253:
        nit = struct.unpack("<H", f.read(2))[0]
    elif nit == 254:
        nit = struct.unpack("<I", f.read(4))[0]
    elif nit == 255:
        nit = struct.unpack("<Q", f.read(8))[0]
    return f.read(nit)

def ser_string(s):
    if len(s) < 253:
        return chr(len(s)) + s
    elif len(s) < 0x10000:
        return chr(253) + struct.pack("<H", len(s)) + s
    elif len(s) < 0x100000000L:
        return chr(254) + struct.pack("<I", len(s)) + s
    return chr(255) + struct.pack("<Q", len(s)) + s

def deser_uint256(f):
    r = 0L
    for i in xrange(8):
        t = struct.unpack("<I", f.read(4))[0]
        r += t << (i * 32)
    return r

def ser_uint256(u):
    rs = ""
    for i in xrange(8):
        rs += struct.pack("<I", u & 0xFFFFFFFFL)
        u >>= 32
    return rs

def uint256_from_str(s):
    r = 0L
    t = struct.unpack("<IIIIIIII", s[:32])
    for i in xrange(8):
        r += t[i] << (i * 32)
    return r

def uint256_from_str_be(s):
    r = 0L
    t = struct.unpack(">IIIIIIII", s[:32])
    for i in xrange(8):
        r += t[i] << (i * 32)
    return r

print uint256_from_str   ("ffffffffffffffffffffffffffffffffffffffffffffffffffffffff00000000")
print uint256_from_str_be("ffffffffffffffffffffffffffffffffffffffffffffffffffffffff00000000")
print uint256_from_str   ("0000000000000000000000000000000000000000000000000000000000000001")
print uint256_from_str_be("0000000000000000000000000000000000000000000000000000000000000001")
