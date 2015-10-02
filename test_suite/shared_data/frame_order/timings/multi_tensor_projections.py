# Python module imports.
from numpy import add, array, diagonal, dot, float64, outer, tensordot, tile, transpose, zeros
from os import pardir, sep
import sys
from timeit import timeit

# Modify the system path.
sys.path.append(pardir+sep+pardir+sep+pardir+sep+pardir+sep)


def proj1(vect, A, N=1, verb=True):
    d = zeros((len(A), len(vect)), float64)
    for iter in range(N):
        for j in range(len(vect)):
            for i in range(len(A)):
                d[i, j] = dot(vect[j], dot(A[i], vect[j]))
    if verb:
        print("\n1st projection - per align, element by element r[j].A[i].r[j].")
        print("Proj1&2: %s, %s" % (d[0, :2], d[1, :2]))


def proj2(vect, A, N=1, verb=True):
    d = zeros((len(A), len(vect)), float64)
    for iter in range(N):
        for i in range(len(A)):
            d[i] = diagonal(tensordot(vect, tensordot(A[i], transpose(vect), axes=1), axes=1))
    if verb:
        print("\n2nd projection - per align, diag of double tensordot.")
        print("Proj1&2: %s, %s" % (d[0, :2], d[1, :2]))


def proj3(vect, A, N=1, verb=True):
    d = zeros((len(A), len(vect)), float64)
    for iter in range(N):
        for i in range(len(A)):
            d[i] = diagonal(tensordot(tensordot(A[i], vect, axes=([0], [1])), vect, axes=([0], [1])))
    if verb:
        print("\n3rd projection - per align, diag of double tensordot, no transpose.")
        print("Proj1&2: %s, %s" % (d[0, :2], d[1, :2]))


def proj4(vect, A, N=1, verb=True):
    d = zeros((len(A), len(vect)), float64)
    for iter in range(N):
        for i in range(len(A)):
            a = tensordot(A[i], vect, axes=([0], [1]))
            for j in range(len(vect)):
                d[i, j] = dot(vect[j], a[:, j])
    if verb:
        print("\n4th projection - per align, mixed tensordot() and per-vector dot().")
        print("Proj1&2: %s, %s" % (d[0, :2], d[1, :2]))


def proj5(vect, A, N=1, verb=True):
    d = zeros((len(A), len(vect)), float64)
    for iter in range(N):
        vect2 = vect**2
        double_vect = 2.0 * vect
        for i in range(len(A)):
            for j in range(len(vect)):
                d[i, j] = vect2[j][0]*A[i, 0, 0] + vect2[j][1]*A[i, 1, 1] + vect2[j][2]*(A[i, 2, 2]) + double_vect[j][0]*vect[j][1]*A[i, 0, 1] + double_vect[j][0]*vect[j][2]*A[i, 0, 2] + double_vect[j][1]*vect[j][2]*A[i, 1, 2]
    if verb:
        print("\n5th projection - per align, expansion and sum.")
        print("Proj1&2: %s, %s" % (d[0, :2], d[1, :2]))


def proj6(vect, A, N=1, verb=True):
    d = zeros((len(A), len(vect)), float64)
    for iter in range(N):
        for i in range(len(A)):
            d[i] = vect[:, 0]**2*A[i, 0, 0] + vect[:, 1]**2*A[i, 1, 1] + vect[:, 2]**2*(A[i, 2, 2]) + 2.0*vect[:, 0]*vect[:, 1]*A[i, 0, 1] + 2.0*vect[:, 0]*vect[:, 2]*A[i, 0, 2] + 2.0*vect[:, 1]*vect[:, 2]*A[i, 1, 2]
    if verb:
        print("\n6th projection - per align, expansion.")
        print("Proj1&2: %s, %s" % (d[0, :2], d[1, :2]))


def proj7(vect, A, N=1, verb=True):
    d = zeros((len(A), len(vect)), float64)
    for iter in range(N):
        vect2 = vect**2
        double_vect = 2.0 * vect
        for i in range(len(A)):
            d[i] = vect2[:, 0]*A[i, 0, 0] + vect2[:, 1]*A[i, 1, 1] + vect2[:, 2]*(A[i, 2, 2]) + double_vect[:, 0]*vect[:, 1]*A[i, 0, 1] + double_vect[:, 0]*vect[:, 2]*A[i, 0, 2] + double_vect[:, 1]*vect[:, 2]*A[i, 1, 2]
    if verb:
        print("\n7th projection - per align, expansion with pre-calculation.")
        print("Proj1&2: %s, %s" % (d[0, :2], d[1, :2]))


def proj8(vect, A, N=1, verb=True):
    d = zeros((len(A), len(vect)), float64)
    for iter in range(N):
        vect2 = vect**2
        double_vect = 2.0 * vect
        d[:] = transpose(outer(vect2[:, 0], A[:, 0, 0]) + outer(vect2[:, 1], A[:, 1, 1]) + outer(vect2[:, 2], A[:, 2, 2]) + outer(double_vect[:, 0]*vect[:, 1], A[:, 0, 1]) + outer(double_vect[:, 0]*vect[:, 2], A[:, 0, 2]) + outer(double_vect[:, 1]*vect[:, 2], A[:, 1, 2]))
    if verb:
        print("\n8th projection - expansion with pre-calculation (outer() and transpose()).")
        print("Proj1&2: %s, %s" % (d[0, :2], d[1, :2]))


def proj9(vect, A, N=1, verb=True):
    d = zeros((len(A), len(vect)), float64)
    for iter in range(N):
        vect2 = vect**2
        double_vect = 2.0 * vect
        d[:] = outer(A[:, 0, 0], vect2[:, 0]) + outer(A[:, 1, 1], vect2[:, 1]) + outer(A[:, 2, 2], vect2[:, 2]) + outer(A[:, 0, 1], double_vect[:, 0]*vect[:, 1]) + outer(A[:, 0, 2], double_vect[:, 0]*vect[:, 2]) + outer(A[:, 1, 2], double_vect[:, 1]*vect[:, 2])
    if verb:
        print("\n9th projection - expansion with pre-calculation (only outer()).")
        print("Proj1&2: %s, %s" % (d[0, :2], d[1, :2]))


def proj10(vect, A, N=1, verb=True):
    d = zeros((len(A), len(vect)), float64)
    for iter in range(N):
        d[:] = 0.0
        vect2 = vect**2
        double_vect = 2.0 * vect
        add(outer(A[:, 0, 0], vect2[:, 0]), d, d)
        add(outer(A[:, 1, 1], vect2[:, 1]), d, d)
        add(outer(A[:, 2, 2], vect2[:, 2]), d, d)
        add(outer(A[:, 0, 1], double_vect[:, 0]*vect[:, 1]), d, d)
        add(outer(A[:, 0, 2], double_vect[:, 0]*vect[:, 2]), d, d)
        add(outer(A[:, 1, 2], double_vect[:, 1]*vect[:, 2]), d, d)
    if verb:
        print("\n10th projection - expansion with pre-calculation (outer() and add()).")
        print("Proj1&2: %s, %s" % (d[0, :2], d[1, :2]))


# Some 200 vectors.
vect = array([[1, 2, 3], [2, 2, 2]], float64)
vect = tile(vect, (100, 1))
if __name__ == '__main__':
    print("Original vectors:\n%s\nShape: %s" % (vect[:2], vect.shape))

# Init the 5 alignment tensors.
A = zeros((3, 3), float64)
A_5D = [1.42219822168827662867e-04, -1.44543001566521341940e-04, -7.07796211648713973798e-04, -6.01619494082773244303e-04, 2.02008007072950861996e-04]
A[0, 0] = A_5D[0]
A[1, 1] = A_5D[1]
A[2, 2] = -A_5D[0] -A_5D[1]
A[0, 1] = A[1, 0] = A_5D[2]
A[0, 2] = A[2, 0] = A_5D[3]
A[1, 2] = A[2, 1] = A_5D[4]
A = tile(A, (5, 1, 1))
A[0] *= 1e4
A[1] *= 2e4
A[2] *= 3e4
A[3] *= 4e4
A[4] *= 5e4
if __name__ == '__main__':
    print("\nTensors:\n%s\n" % A)

# Projections.
N = 100
M = 100
if __name__ == '__main__':
    proj1(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj1(vect=vect, A=A, N=N, verb=False)", setup="from multi_tensor_projections import proj1, vect, A, N", number=M))

    proj2(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj2(vect=vect, A=A, N=N, verb=False)", setup="from multi_tensor_projections import proj2, vect, A, N", number=M))

    proj3(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj3(vect=vect, A=A, N=N, verb=False)", setup="from multi_tensor_projections import proj3, vect, A, N", number=M))

    proj4(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj4(vect=vect, A=A, N=N, verb=False)", setup="from multi_tensor_projections import proj4, vect, A, N", number=M))

    proj5(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj5(vect=vect, A=A, N=N, verb=False)", setup="from multi_tensor_projections import proj5, vect, A, N", number=M))

    proj6(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj6(vect=vect, A=A, N=N, verb=False)", setup="from multi_tensor_projections import proj6, vect, A, N", number=M))

    proj7(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj7(vect=vect, A=A, N=N, verb=False)", setup="from multi_tensor_projections import proj7, vect, A, N", number=M))

    proj8(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj8(vect=vect, A=A, N=N, verb=False)", setup="from multi_tensor_projections import proj8, vect, A, N", number=M))

    proj9(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj9(vect=vect, A=A, N=N, verb=False)", setup="from multi_tensor_projections import proj9, vect, A, N", number=M))

    proj10(vect=vect, A=A, N=1, verb=True)
    print("Timing (s): %s" % timeit("proj10(vect=vect, A=A, N=N, verb=False)", setup="from multi_tensor_projections import proj10, vect, A, N", number=M))
