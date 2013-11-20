# Eloipool - Python Bitcoin pool server
# Copyright (C) 2011-2012  Luke Dashjr <luke-jr+eloipool@utopios.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from hashlib import sha256
from util import doublesha

class MerkleTree:
    def __init__(self, data, detailed=False):
        self.data = data
        self.recalculate(detailed)
        self._hash_steps = None
    
    def recalculate(self, detailed=False):
        L = self.data
        steps = []
        if detailed:
            detail = []
            PreL = []
            StartL = 0
        else:
            detail = None
            PreL = [None]
            StartL = 2
        Ll = len(L)
        if detailed or Ll > 1:
            while True:
                if detailed:
                    detail += L
                if Ll == 1:
                    break
                steps.append(L[1])
                if Ll % 2:
                    L += [L[-1]]
                L = PreL + [doublesha(L[i] + L[i + 1]) for i in range(StartL, Ll, 2)]
                Ll = len(L)
        self._steps = steps
        self.detail = detail
    
    def hash_steps(self):
        if self._hash_steps == None:
            self._hash_steps = doublesha(''.join(self._steps))
        return self._hash_steps
        
    def withFirst(self, f):
        steps = self._steps
        for s in steps:
            f = doublesha(f + s)
        return f
    
    def merkleRoot(self):
        return self.withFirst(self.data[0])

# MerkleTree tests
def _test():
    import binascii
    import time    
        
    mt = MerkleTree([None] + [binascii.unhexlify(a) for a in [
        '999d2c8bb6bda0bf784d9ebeb631d711dbbbfe1bc006ea13d6ad0d6a2649a971',
        '3f92594d5a3d7b4df29d7dd7c46a0dac39a96e751ba0fc9bab5435ea5e22a19d',
        'a5633f03855f541d8e60a6340fc491d49709dc821f3acb571956a856637adcb6',
        '28d97c850eaf917a4c76c02474b05b70a197eaefb468d21c22ed110afe8ec9e0',
    ]])
    assert(
        b'82293f182d5db07d08acf334a5a907012bbb9990851557ac0ec028116081bd5a' ==
        binascii.b2a_hex(mt.withFirst(binascii.unhexlify('d43b669fb42cfa84695b844c0402d410213faa4f3e66cb7248f688ff19d5e5f7')))
    )
    
    print '82293f182d5db07d08acf334a5a907012bbb9990851557ac0ec028116081bd5a'
    txes = [binascii.unhexlify(a) for a in [
        'd43b669fb42cfa84695b844c0402d410213faa4f3e66cb7248f688ff19d5e5f7',
        '999d2c8bb6bda0bf784d9ebeb631d711dbbbfe1bc006ea13d6ad0d6a2649a971',
        '3f92594d5a3d7b4df29d7dd7c46a0dac39a96e751ba0fc9bab5435ea5e22a19d',
        'a5633f03855f541d8e60a6340fc491d49709dc821f3acb571956a856637adcb6',
        '28d97c850eaf917a4c76c02474b05b70a197eaefb468d21c22ed110afe8ec9e0',
    ]]
             
    s = time.time()
    mt = MerkleTree(txes)
    for x in range(100):
        y = int('d43b669fb42cfa84695b844c0402d410213faa4f3e66cb7248f688ff19d5e5f7', 16)
        #y += x
        coinbasehash = binascii.unhexlify("%x" % y)
        x = binascii.b2a_hex(mt.withFirst(coinbasehash))

    print x
    print time.time() - s

if __name__ == '__main__':
    _test()
