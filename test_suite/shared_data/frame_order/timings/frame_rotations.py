###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Python module imports.
from numpy import array, dot, float64, swapaxes, tensordot, tile, transpose, zeros
from os import pardir, sep
import sys
from timeit import timeit

# Modify the system path.
sys.path.append(pardir+sep+pardir+sep+pardir+sep+pardir+sep)

# relax module imports.
from lib.geometry.rotations import euler_to_R_zyz


def rot1(Ri, R, RT, N=1, verb=True):
    d = zeros((len(Ri), 3, 3), float64)
    for i in range(N):
        for j in range(len(Ri)):
            d[j] = dot(R, dot(Ri[j], RT))
    if verb:
        print("\n1st rotation - element by element R.Ri[i].RT.")
        print("Rotations:\n%s" % d[:2])


def rot2(Ri, R, RT, N=1, verb=True):
    for i in range(N):
        d = dot(R, tensordot(Ri, RT, axes=1))
        d = swapaxes(d, 0, 1)
    if verb:
        print("\n2nd rotation - dot of tensordot, and axis swap.")
        print("Rotations:\n%s" % d[:2])


# Some 200 3D matrices.
Ri = array([[1, 2, 3], [2, 3, 4], [3, 4, 5]], float64)
Ri = tile(Ri, (100, 1, 1))
if __name__ == '__main__':
    print("Original matrices:\n%s\nShape: %s" % (Ri[:2], Ri.shape))

# The rotation matrix.
R = zeros((3, 3), float64)
RT = transpose(R)
euler_to_R_zyz(1, 1, 0.5, R)
if __name__ == '__main__':
    print("\nR:\n%s\n" % R)

# Projections.
N = 1000
M = 100
if __name__ == '__main__':
    rot1(Ri=Ri, R=R, RT=RT, N=1, verb=True)
    print("Timing (s): %s" % timeit("rot1(Ri=Ri, R=R, RT=RT, N=N, verb=False)", setup="from frame_rotations import rot1, Ri, R, RT, N", number=M))

    rot2(Ri=Ri, R=R, RT=RT, N=1, verb=True)
    print("Timing (s): %s" % timeit("rot2(Ri=Ri, R=R, RT=RT, N=N, verb=False)", setup="from frame_rotations import rot2, Ri, R, RT, N", number=M))
