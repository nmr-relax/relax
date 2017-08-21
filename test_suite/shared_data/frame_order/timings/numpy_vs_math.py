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
import math
import numpy
from timeit import timeit


def test_math(N=1):
    for i in range(N):
        math.cos(0.1)

def test_numpy(N=1):
    for i in range(N):
        numpy.cos(0.1)


N = 10000
M = 1000
if __name__ == '__main__':
    test_math(N=1)
    print("Timing (s): %s" % timeit("test_math(N=N)", setup="from numpy_vs_math import math, test_math, N", number=M))

    test_numpy(N=1)
    print("Timing (s): %s" % timeit("test_numpy(N=N)", setup="from numpy_vs_math import numpy, test_numpy, N", number=M))
