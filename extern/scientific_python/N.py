from numpy.oldnumeric import *
def int_sum(a, axis=0):
    return add.reduce(a, axis)
def zeros_st(shape, other):
    return zeros(shape, dtype=other.dtype)
from numpy import ndarray as array_type
