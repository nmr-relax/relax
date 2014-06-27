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
"""Module for the calculation of the matrix power, for higher dimensional data."""

# Python module imports.
from numpy.lib.stride_tricks import as_strided
from numpy import float64, int16, zeros
from numpy.linalg import matrix_power


def create_index(data):
    """ Method to create the helper index matrix, to help figuring out the index to store in the data matrix. """

    # Extract shapes from data.
    NE, NS, NM, NO, ND, Row, Col = data.shape

    # Make array to store index.
    index = zeros([NE, NS, NM, NO, ND, 5], int16)

    for ei in range(NE):
        for si in range(NS):
            for mi in range(NM):
                for oi in range(NO):
                    for di in range(ND):
                        index[ei, si, mi, oi, di] = ei, si, mi, oi, di

    return index


def matrix_power_strided_rank_NE_NS_NM_NO_ND_x_x(data, power):
    """Calculate the exact matrix power by striding through higher dimensional data.  This of dimension [NE][NS][NM][NO][ND][X][X].

    Here X is the Row and Column length, of the outer square matrix.

    @param data:        The square matrix to calculate the matrix exponential of.
    @type data:         numpy float array of rank [NE][NS][NM][NO][ND][X][X]
    @keyword power:     The matrix exponential power array, which hold the power integer to which to raise the outer matrix X,X to.
    @type power:        numpy int array of rank [NE][NS][NM][NO][ND]
    @return:            The matrix pwer.  This will have the same dimensionality as the data matrix.
    @rtype:             numpy float array of rank [NE][NS][NM][NO][ND][X][X]
    """

    # Extract shapes from data.
    NE, NS, NM, NO, ND, Row, Col = data.shape

    # Make array to store results
    calc = zeros([NE, NS, NM, NO, ND, Row, Col], float64)

    # Get the data view, from the helper function.
    data_view = stride_help_square_matrix_rank_NE_NS_NM_NO_ND_x_x(data)

    # Get the power view, from the helper function.
    power_view = stride_help_element_rank_NE_NS_NM_NO_ND(power)

    # The index view could be pre formed in init.
    index = create_index(data)
    index_view = stride_help_array_rank_NE_NS_NM_NO_ND_x(index)

    # Zip them together and iterate over them.
    for data_i, power_i, index_i in zip(data_view, power_view, index_view):
        # Do power calculation with numpy method.
        data_power_i = matrix_power(data_i, int(power_i))

        # Extract index from index_view.
        ei, si, mi, oi, di = index_i

        # Store the result.
        calc[ei, si, mi, oi, di, :] = data_power_i

    return calc


def stride_help_array_rank_NE_NS_NM_NO_ND_x(data):
    """ Method to stride through the data matrix, extracting the outer array with nr of elements as Column length. """

    # Extract shapes from data.
    NE, NS, NM, NO, ND, Col = data.shape

    # Calculate how many small matrices.
    Nr_mat = NE * NS * NM * NO * ND

    # Define the shape for the stride view.
    shape = (Nr_mat, Col)

    # Get itemsize, Length of one array element in bytes. Depends on dtype. float64=8, complex128=16.
    itz = data.itemsize

    # Bytes_between_elements
    bbe = 1 * itz

    # Bytes between row. The distance in bytes to next row is number of Columns elements multiplied with itemsize.
    bbr = Col * itz

    # Make a tuple of the strides.
    strides = (bbr, bbe)

    # Make the stride view.
    data_view = as_strided(data, shape=shape, strides=strides)

    return data_view


def stride_help_element_rank_NE_NS_NM_NO_ND(data):
    """ Method to stride through the data matrix, extracting the outer element. """

    # Extract shapes from data.
    NE, NS, NM, NO, Col = data.shape

    # Calculate how many small matrices.
    Nr_mat = NE * NS * NM * NO * Col

    # Define the shape for the stride view.
    shape = (Nr_mat, 1)

    # Get itemsize, Length of one array element in bytes. Depends on dtype. float64=8, complex128=16.
    itz = data.itemsize

    # FIXME: Explain this.
    bbe = Col * itz

    # FIXME: Explain this.
    bbr = 1 * itz

    # Make a tuple of the strides.
    strides = (bbr, bbe)

    # Make the stride view.
    data_view = as_strided(data, shape=shape, strides=strides)

    return data_view


def stride_help_square_matrix_rank_NE_NS_NM_NO_ND_x_x(data):
    """ Helper function calculate the strides to go through the data matrix, extracting the outer Row X Col matrix. """

    # Extract shapes from data.
    NE, NS, NM, NO, ND, Row, Col = data.shape

    # Calculate how many small matrices.
    Nr_mat = NE * NS * NM * NO * ND

    # Define the shape for the stride view.
    shape = (Nr_mat, Row, Col)

    # Get itemsize, Length of one array element in bytes. Depends on dtype. float64=8, complex128=16.
    itz = data.itemsize

    # Bytes_between_elements
    bbe = 1 * itz

    # Bytes between row. The distance in bytes to next row is number of Columns elements multiplied with itemsize.
    bbr = Col * itz

    # Bytes between matrices.  The byte distance is separated by the number of rows.
    bbm = Row * Col * itz

    # Make a tuple of the strides.
    strides = (bbm, bbr, bbe)

    # Make the stride view.
    data_view = as_strided(data, shape=shape, strides=strides)

    return data_view

