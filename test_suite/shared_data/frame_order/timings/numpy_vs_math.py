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
