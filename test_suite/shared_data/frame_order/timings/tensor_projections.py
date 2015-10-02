# Python module imports.
from numpy import *
from numpy.linalg import norm
from os import pardir, sep
import sys
from time import sleep
from timeit import timeit

# Modify the system path.
sys.path.append(pardir+sep+pardir+sep+pardir+sep+pardir+sep)

# relax module imports.
from lib.geometry.rotations import euler_to_R_zyz


def proj1(vect, A, N=1, verb=True):
    d = zeros(len(vect), float64)
    for i in range(N):
        for j in xrange(len(vect)):
            d[j] = dot(vect[j], dot(A, vect[j]))
    if verb:
        print("\n1st projection - element by element r[i].A.r[i].")
        print("Proj: %s" % d[:2])


def proj2(vect, A, N=1, verb=True):
    for i in range(N):
        d = diagonal(tensordot(vect, tensordot(A, transpose(vect), axes=1), axes=1))
    if verb:
        print("\n2nd projection - diag of double tensordot.")
        print("Proj: %s" % d[:2])


def proj3(vect, A, N=1, verb=True):
    for i in range(N):
        d = diagonal(tensordot(tensordot(A, vect, axes=([0], [1])), vect, axes=([0], [1])))
    if verb:
        print("\n3rd projection - diag of double tensordot, no transpose.")
        print("Proj: %s" % d[:2])


def proj4(vect, A, N=1, verb=True):
    d = zeros(len(vect), float64)
    for i in range(N):
        a = tensordot(A, vect, axes=([0], [1]))
        for j in range(len(vect)):
            d[j] = dot(vect[j], a[:, j])
    if verb:
        print("\n4th projection - mixed tensordot() and per-vector dot().")
        print("Proj: %s" % d[:2])


def proj5(vect, A, N=1, verb=True):
    d = zeros(len(vect), float64)
    for i in range(N):
        vect2 = vect**2
        double_vect = 2.0 * vect
        for j in xrange(len(vect)):
            d[j] = vect2[j][0]*A[0, 0] + vect2[j][1]*A[1, 1] + vect2[j][2]*(A[2, 2]) + double_vect[j][0]*vect[j][1]*A[0, 1] + double_vect[j][0]*vect[j][2]*A[0, 2] + double_vect[j][1]*vect[j][2]*A[1, 2]
    if verb:
        print("\n5th projection - expansion and sum.")
        print("Proj: %s" % d[:2])


def proj6(vect, A, N=1, verb=True):
    d = zeros(len(vect), float64)
    for i in range(N):
        d = vect[:, 0]**2*A[0, 0] + vect[:, 1]**2*A[1, 1] + vect[:, 2]**2*(A[2, 2]) + 2.0*vect[:, 0]*vect[:, 1]*A[0, 1] + 2.0*vect[:, 0]*vect[:, 2]*A[0, 2] + 2.0*vect[:, 1]*vect[:, 2]*A[1, 2]
    if verb:
        print("\n6th projection - expansion.")
        print("Proj: %s" % d[:2])


def proj7(vect, A, N=1, verb=True):
    d = zeros(len(vect), float64)
    for i in range(N):
        vect2 = vect**2
        double_vect = 2.0 * vect
        d = vect2[:, 0]*A[0, 0] + vect2[:, 1]*A[1, 1] + vect2[:, 2]*(A[2, 2]) + double_vect[:, 0]*vect[:, 1]*A[0, 1] + double_vect[:, 0]*vect[:, 2]*A[0, 2] + double_vect[:, 1]*vect[:, 2]*A[1, 2]
    if verb:
        print("\n7th projection - expansion with pre-calculation.")
        print("Proj: %s" % d[:2])


# Some 200 vectors.
vect = array([[1, 2, 3], [2, 2, 2]], float64)
vect = tile(vect, (100, 1))
if __name__ == '__main__':
    print("Original vectors:\n%s\nShape: %s" % (vect[:2], vect.shape))

# Init the alignment tensor.
A = zeros((3, 3), float64)
A_5D = [1.42219822168827662867e-04, -1.44543001566521341940e-04, -7.07796211648713973798e-04, -6.01619494082773244303e-04, 2.02008007072950861996e-04]
A[0, 0] = A_5D[0]
A[1, 1] = A_5D[1]
A[2, 2] = -A_5D[0] -A_5D[1]
A[0, 1] = A[1, 0] = A_5D[2]
A[0, 2] = A[2, 0] = A_5D[3]
A[1, 2] = A[2, 1] = A_5D[4]
A *= 1e4
if __name__ == '__main__':
    print("\nTensor:\n%s\n" % A)

# Projections.
N = 100
M = 100
if __name__ == '__main__':
    proj1(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj1(vect=vect, A=A, N=N, verb=False)", setup="from tensor_projections import proj1, vect, A, N", number=M))

    proj2(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj2(vect=vect, A=A, N=N, verb=False)", setup="from tensor_projections import proj2, vect, A, N", number=M))

    proj3(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj3(vect=vect, A=A, N=N, verb=False)", setup="from tensor_projections import proj3, vect, A, N", number=M))

    proj4(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj4(vect=vect, A=A, N=N, verb=False)", setup="from tensor_projections import proj4, vect, A, N", number=M))

    proj5(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj5(vect=vect, A=A, N=N, verb=False)", setup="from tensor_projections import proj5, vect, A, N", number=M))

    proj6(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj6(vect=vect, A=A, N=N, verb=False)", setup="from tensor_projections import proj6, vect, A, N", number=M))

    proj7(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj7(vect=vect, A=A, N=N, verb=False)", setup="from tensor_projections import proj7, vect, A, N", number=M))
