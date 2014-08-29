###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

# Module docstring.
"""Module for the calculation of the matrix exponential, for higher dimensional data."""

# Python module imports.
from numpy import array, any, complex128, dot, einsum, eye, exp, iscomplex, int16, newaxis, multiply, tile, sqrt, version, zeros
from numpy.lib.stride_tricks import as_strided
from numpy.linalg import eig, inv


def create_index(NE=None, NS=None, NM=None, NO=None, ND=None):
    """Method to create the helper index numpy array, to help figuring out the indices to store in the exchange data matrix.

    @keyword NE:  The total number of experiment types.
    @type NE:     None or int
    @keyword NS:  The total number of spins of the spin cluster.
    @type NS:     int
    @keyword NM:  The total number of magnetic field strengths.
    @type NM:     int
    @keyword NO:  The total number of spin-lock offsets.
    @type NO:     int
    @keyword ND:  The total number of dispersion points (either the spin-lock field strength or the nu_CPMG frequency).
    @type ND:     int
    @return:      The numpy array for containing index indices for storing in the strided exchange data matrix.
    @rtype:       numpy int array of rank [NE][NS][NM][NO][ND][5] or [NS][NM][NO][ND][4].
    """

    # Make array to store index.
    if NE != None:
        index = zeros([NE, NS, NM, NO, ND, 5], int16)

    else:
        index = zeros([NS, NM, NO, ND, 4], int16)

    # Make indices for storing in data matrix.
    if NE != None:
        for ei in range(NE):
            for si in range(NS):
                for mi in range(NM):
                    for oi in range(NO):
                        for di in range(ND):
                            index[ei, si, mi, oi, di] = ei, si, mi, oi, di

    else:
        for si in range(NS):
            for mi in range(NM):
                for oi in range(NO):
                    for di in range(ND):
                        index[si, mi, oi, di] = si, mi, oi, di

    return index


def data_view_via_striding_array_col(data_array=None):
    """Method to stride through the data matrix, extracting the outer array with nr of elements as Column length.

    @keyword data:  The numpy data array to stride through.
    @type data:     numpy array of rank [NE][NS][NM][NO][ND][Col] or [NS][NM][NO][ND][Col].
    @return:        The data view of the full numpy array, returned as a numpy array with number of small numpy arrays corresponding to Nr_mat=NE*NS*NM*NO*ND or Nr_mat=NS*NM*NO*ND, where each small array has size Col.
    @rtype:         numpy array of rank [NE*NS*NM*NO*ND][Col] or [NS*NM*NO*ND][Col].
    """

    # Get the expected shape of the higher dimensional column numpy array.
    if len(data_array.shape) == 6:
        # Extract shapes from data.
        NE, NS, NM, NO, ND, Col = data_array.shape

    else:
        # Extract shapes from data.
        NS, NM, NO, ND, Col = data_array.shape

        # Set NE to 1.
        NE = 1

    # Calculate how many small matrices.
    Nr_mat = NE * NS * NM * NO * ND

    # Define the shape for the stride view.
    shape = (Nr_mat, Col)

    # Get itemsize, Length of one array element in bytes. Depends on dtype. float64=8, complex128=16.
    itz = data_array.itemsize

    # Bytes_between_elements
    bbe = 1 * itz

    # Bytes between row. The distance in bytes to next row is number of Columns elements multiplied with itemsize.
    bbr = Col * itz

    # Make a tuple of the strides.
    strides = (bbr, bbe)

    # Make the stride view.
    data_view = as_strided(data_array, shape=shape, strides=strides)

    return data_view


def data_view_via_striding_array_row_col(data_array=None):
    """Method to stride through the data matrix, extracting the outer matrix with nr of elements as Row X Column length.  Row and Col should have same size.

    @keyword data:  The numpy data array to stride through.
    @type data:     numpy array of rank [NE][NS][NM][NO][ND][Row][Col] or [NS][NM][NO][ND][Row][Col].
    @return:        The data view of the full numpy array, returned as a numpy array with number of small numpy arrays corresponding to Nr_mat=NE*NS*NM*NO*ND or Nr_mat=NS*NM*NO*ND, where each small array has size Col.
    @rtype:         numpy array of rank [NE*NS*NM*NO*ND][Col] or [NS*NM*NO*ND][Col].
    """

    # Get the expected shape of the higher dimensional column numpy array.
    if len(data_array.shape) == 7:
        # Extract shapes from data.
        NE, NS, NM, NO, ND, Row, Col = data_array.shape

    else:
        # Extract shapes from data.
        NS, NM, NO, ND, Row, Col = data_array.shape

        # Set NE to 1.
        NE = 1

    # Calculate how many small matrices.
    Nr_mat = NE * NS * NM * NO * ND

    # Define the shape for the stride view.
    shape = (Nr_mat, Row, Col)

    # Get itemsize, Length of one array element in bytes. Depends on dtype. float64=8, complex128=16.
    itz = data_array.itemsize

    # Bytes_between_elements
    bbe = 1 * itz

    # Bytes between row. The distance in bytes to next row is number of Columns elements multiplied with itemsize.
    bbr = Col * itz

    # Bytes between matrices.  The byte distance is separated by the number of rows.
    bbm = Row * bbr

    # Make a tuple of the strides.
    strides = (bbm, bbr, bbe)

    # Make the stride view.
    data_view = as_strided(data_array, shape=shape, strides=strides)

    return data_view


def matrix_exponential(A, dtype=None):
    """Calculate the exact matrix exponential using the eigenvalue decomposition approach, for higher dimensional data.  This of dimension [NE][NS][NM][NO][ND][X][X] or [NS][NM][NO][ND][X][X].

    Here X is the Row and Column length, of the outer square matrix.

    @param A:               The square matrix to calculate the matrix exponential of.
    @type A:                numpy float array of rank [NE][NS][NM][NO][ND][X][X]
    @param dtype:           If provided, forces the calculation to use the data type specified.
    @type dtype:            data-type, optional
    @return:                The matrix exponential.  This will have the same dimensionality as the A matrix.
    @rtype:                 numpy float array of rank [NE][NS][NM][NO][ND][X][X]
    """

    # Get the expected shape of the higher dimensional column numpy array.
    if len(A.shape) == 7:
        # Extract shapes from data.
        NE, NS, NM, NO, ND, Row, Col = A.shape

    else:
        # Extract shapes from data.
        NS, NM, NO, ND, Row, Col = A.shape

        # Set NE to None.
        NE = None

    # Convert dtype, if specified.
    if dtype != None:
        dtype_mat = A.dtype

        # If the dtype is different from the input.
        if dtype_mat != dtype:
            # This needs to be made as a copy.
            A = A.astype(dtype)

    # Is the original matrix real?
    complex_flag = any(iscomplex(A))

    # If numpy is under 1.8, there would be a need to do eig(A) per matrix.
    if float(version.version[:3]) < 1.8:
        # Make array to store results
        if NE != None:
            if dtype != None:
                eA = zeros([NE, NS, NM, NO, ND, Row, Col], dtype=dtype)
            else:
                eA = zeros([NE, NS, NM, NO, ND, Row, Col], dtype=complex128)
        else:
            if dtype != None:
                eA = zeros([NS, NM, NO, ND, Row, Col], dtype=dtype)
            else:
                eA = zeros([NS, NM, NO, ND, Row, Col], dtype=complex128)

        # Get the data view, from the helper function.
        A_view = data_view_via_striding_array_row_col(data_array=A)

        # Create index view.
        index = create_index(NE=NE, NS=NS, NM=NM, NO=NO, ND=ND)
        index_view = data_view_via_striding_array_col(data_array=index)

        # Zip them together and iterate over them.
        for A_i, index_i in zip(A_view, index_view):
            # The eigenvalue decomposition.
            W_i, V_i = eig(A_i)

            # Calculate the exponential.
            W_exp_i = exp(W_i)

            # Make a eye matrix.
            eye_mat_i = eye(Row)

            # Transform it to a diagonal matrix, with elements from vector down the diagonal.
            # Use the dtype, if specified.
            if dtype != None:
                W_exp_diag_i = multiply(W_exp_i, eye_mat_i, dtype=dtype )
            else:
                W_exp_diag_i = multiply(W_exp_i, eye_mat_i)

            # Make dot product.
            dot_V_W_i = dot( V_i, W_exp_diag_i)

            # Compute the (multiplicative) inverse of a matrix.
            inv_V_i = inv(V_i)

            # Calculate the exact exponential.
            eA_i = dot(dot_V_W_i, inv_V_i)

            # Save results.
            # Extract index from index_view.
            if NE != None:
                ei, si, mi, oi, di = index_i
                eA[ei, si, mi, oi, di, :] = eA_i
            else:
                si, mi, oi, di = index_i
                eA[si, mi, oi, di, :] = eA_i

    else:
        # The eigenvalue decomposition.
        W, V = eig(A)

        # W: The eigenvalues, each repeated according to its multiplicity.
        # The eigenvalues are not necessarily ordered.
        # The resulting array will be always be of complex type. Shape [NE][NS][NM][NO][ND][X]
        # V: The normalized (unit 'length') eigenvectors, such that the column v[:,i]
        # is the eigenvector corresponding to the eigenvalue w[i]. Shape [NE][NS][NM][NO][ND][X][X]

        # Calculate the exponential of all elements in the input array. Shape [NE][NS][NM][NO][ND][X]
        # Add one axis, to allow for broadcasting multiplication.
        if NE != None:
            W_exp = exp(W).reshape(NE, NS, NM, NO, ND, Row, 1)
        else:
            W_exp = exp(W).reshape(NS, NM, NO, ND, Row, 1)

        # Make a eye matrix, with Shape [NE][NS][NM][NO][ND][X][X]
        if NE != None:
            eye_mat = tile(eye(Row)[newaxis, newaxis, newaxis, newaxis, newaxis, ...], (NE, NS, NM, NO, ND, 1, 1) )
        else:
            eye_mat = tile(eye(Row)[newaxis, newaxis, newaxis, newaxis, ...], (NS, NM, NO, ND, 1, 1) )

        # Transform it to a diagonal matrix, with elements from vector down the diagonal.
        # Use the dtype, if specified.
        if dtype != None:
            W_exp_diag = multiply(W_exp, eye_mat, dtype=dtype )
        else:
            W_exp_diag = multiply(W_exp, eye_mat)

        # Make dot products for higher dimension.
        # "...", the Ellipsis notation, is designed to mean to insert as many full slices (:)
        # to extend the multi-dimensional slice to all dimensions.
        dot_V_W = einsum('...ij, ...jk', V, W_exp_diag)

        # Compute the (multiplicative) inverse of a matrix.
        inv_V = inv(V)

        # Calculate the exact exponential.
        eA = einsum('...ij, ...jk', dot_V_W, inv_V)

    # Return the complex matrix.
    if complex_flag:
        return array(eA)

    # Return only the real part.
    else:
        return array(eA.real)


def matrix_exponential_rank_NS_NM_NO_ND_2_2(A, dtype=None):
    """Calculate the exact matrix exponential using the closed form in terms of the matrix elements., for higher dimensional data.  This is of dimension [NS][NM][NO][ND][2][2].

    Here X is the Row and Column length, of the outer square matrix.

    @param A:       The square matrix to calculate the matrix exponential of.
    @type A:        numpy float array of rank [NS][NM][NO][ND][2][2]
    @param dtype:   If provided, forces the calculation to use the data type specified.
    @type dtype:    data-type, optional
    @return:        The matrix exponential.  This will have the same dimensionality as the A matrix.
    @rtype:         numpy float array of rank [NS][NM][NO][ND][2][2]
    """

    # Extract shapes from data.
    NS, NM, NO, ND, Row, Col = A.shape

    # Convert dtype, if specified.
    if dtype != None:
        dtype_mat = A.dtype

        # If the dtype is different from the input.
        if dtype_mat != dtype:
            # This needs to be made as a copy.
            A = A.astype(dtype)

    # Is the original matrix real?
    complex_flag = any(iscomplex(A))

    # Make array to store results
    if dtype != None:
        eA_mat = zeros([NS, NM, NO, ND, Row, Col], dtype)
    else:
        eA_mat = zeros([NS, NM, NO, ND, Row, Col], dtype)

    # Get the data view, from the helper function.
    A_view = data_view_via_striding_array_row_col(data_array=A)

    # The index view could be pre formed in init.
    index = create_index(NS=NS, NM=NM, NO=NO, ND=ND)
    index_view = data_view_via_striding_array_col(data_array=index)

    # Zip them together and iterate over them.
    for A_i, index_i in zip(A_view, index_view):
        a11 = A_i[0, 0]
        a12 = A_i[0, 1]
        a21 = A_i[1, 0]
        a22 = A_i[1, 1]

        # Discriminant
        a = 1
        b = -a11 - a22
        c = a11 * a22 - a12 * a21
        dis = b**2 - 4*a*c

        # If dis is positive: two distinct real roots
        # If dis is zero: one distinct real roots
        # If dis is negative: two complex roots

        # Eigenvalues lambda_1, lambda_2.
        l1 = (-b + dis) / (2*a)
        l2 = (-b - dis) / (2*a)

        # Define M: M = V^-1 * [ [l1 0], [0 l2] ] * V
        W_m = array([ [l1, 0], [0, l2] ])

        v1_1 = 1
        v1_2 = (l1 - a11) / a12

        v2_1 = 1
        v2_2 = (l2 - a11) / a12

        # normalized eigenvector
        v1_1_norm = v1_1 / (sqrt(v1_1**2 + v1_2**2) )
        v1_2_norm = v1_2 / (sqrt(v1_1**2 + v1_2**2) )
        v2_1_norm = v2_1 / (sqrt(v2_1**2 + v2_2**2) )
        v2_2_norm = v2_2 / (sqrt(v2_1**2 + v2_2**2) )

        #V_m = array([ [v1_norm], [v2_norm] ])
        V_m = array([ [v1_1_norm, v2_1_norm], [v1_2_norm, v2_2_norm] ])

        V_inv_m = inv(V_m)

        # Calculate the exact exponential.
        dot_V_W = dot(V_m, W_m)
        eA_m = dot(dot_V_W, V_inv_m)

        # Save results.

        # Extract index from index_view.
        si, mi, oi, di = index_i

        # Store the result.
        eA_mat[si, mi, oi, di, :] = eA_m

    return eA_mat
