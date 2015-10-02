# Python module imports.
from numpy import array
from os import pardir, sep
import sys
from timeit import timeit

# Modify the system path.
sys.path.append(pardir+sep+pardir+sep+pardir+sep+pardir+sep)


def check1(flags, N=1, verb=True):
    for i in range(N):
        flag = False
        if 0 in flags:
            flag = True
    if verb:
        print("\n1st check - 0 in flags.")
        print("Zeros present: %s" % flag)


def check2(flags, N=1, verb=True):
    for i in range(N):
        flag = False
        if min(flags) == 0:
            flag = True
    if verb:
        print("\n2nd check - min(flags).")
        print("Zeros present: %s" % flag)


def check3(flags, N=1, verb=True):
    for i in range(N):
        flag = False
        if flags.min() == 0:
            flag = True
    if verb:
        print("\n3rd check - flags.min().")
        print("Zeros present: %s" % flag)


def check4(flags, N=1, verb=True):
    for i in range(N):
        flag = False
        if sum(flags) > 0:
            flag = True
    if verb:
        print("\n4th check - sum(flags).")
        print("Zeros present: %s" % flag)


def check5(flags, N=1, verb=True):
    for i in range(N):
        flag = False
        for i in range(len(flags)):
            if flags[i] == 0:
                flag = True
                break
    if verb:
        print("\n5th check - for loop.")
        print("Zeros present: %s" % flag)


def check6(flags, N=1, verb=True):
    for i in range(N):
        flag = False
        if not flags.all():
            flag = True
    if verb:
        print("\n6th check - not flags.all().")
        print("Zeros present: %s" % flag)


def check7(flags, N=1, verb=True):
    pre = False
    if min(flags) == 0:
        pre = True
    for i in range(N):
        flag = False
        if pre:
            flag = True
    if verb:
        print("\n7th check - pre-convert to single flag.")
        print("Zeros present: %s" % flag)


# Flag array.
flags = array([0, 1, 1, 0, 1])

# Checks.
N = 10000
M = 100
if __name__ == '__main__':
    check1(flags=flags, N=1, verb=True)
    print("Timing (s): %s" % timeit("check1(flags=flags, N=N, verb=False)", setup="from flag_array import check1, flags, N", number=M))

    check2(flags=flags, N=1, verb=True)
    print("Timing (s): %s" % timeit("check2(flags=flags, N=N, verb=False)", setup="from flag_array import check2, flags, N", number=M))

    check3(flags=flags, N=1, verb=True)
    print("Timing (s): %s" % timeit("check3(flags=flags, N=N, verb=False)", setup="from flag_array import check3, flags, N", number=M))

    check4(flags=flags, N=1, verb=True)
    print("Timing (s): %s" % timeit("check4(flags=flags, N=N, verb=False)", setup="from flag_array import check4, flags, N", number=M))

    check5(flags=flags, N=1, verb=True)
    print("Timing (s): %s" % timeit("check5(flags=flags, N=N, verb=False)", setup="from flag_array import check5, flags, N", number=M))

    check6(flags=flags, N=1, verb=True)
    print("Timing (s): %s" % timeit("check6(flags=flags, N=N, verb=False)", setup="from flag_array import check6, flags, N", number=M))

    check7(flags=flags, N=1, verb=True)
    print("Timing (s): %s" % timeit("check7(flags=flags, N=N, verb=False)", setup="from flag_array import check7, flags, N", number=M))
