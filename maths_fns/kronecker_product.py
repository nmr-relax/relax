from numpy import concatenate, outer


def kron_prod(A, B):
    """Calculate the Kronecker product of the matrices A and B.

    @param A:   ixj matrix.
    @type A:    rank-2 numpy array
    @param B:   kxl matrix.
    @type B:    rank-2 numpy array
    @return:    The Kronecker product.
    @rtype:     ikxjl rank-2 numpy array
    """

    # The outer product.
    C = outer(A, B)

    # Redefine the shape.
    C.shape = A.shape + B.shape

    # Generate and return the Kronecker product matrix.
    return concatenate(concatenate(C, axis=1), axis=1)
