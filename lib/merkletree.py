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
