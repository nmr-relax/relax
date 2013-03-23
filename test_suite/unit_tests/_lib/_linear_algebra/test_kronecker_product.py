###############################################################################
#                                                                             #
# Copyright (C) 2009-2013 Edward d'Auvergne                                   #
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
from numpy import array, eye, float64, zeros
from sys import stdout
from unittest import TestCase

# relax module imports.
from lib.linear_algebra.kronecker_product import *


class Test_kronecker_product(TestCase):
    """Unit tests for the target_functions.kronecker_product relax module."""

    def setUp(self):
        """Set up data used by the unit tests."""

        # A rank-4, 3D tensor in string form (and rank-2, 9D).
        self.daeg_str = [
            ['0000', '0001', '0002',   '0010', '0011', '0012',  '0020', '0021', '0022'],
            ['0100', '0101', '0102',   '0110', '0111', '0112',  '0120', '0121', '0122'],
            ['0200', '0201', '0202',   '0210', '0211', '0212',  '0220', '0221', '0222'],

            ['1000', '1001', '1002',   '1010', '1011', '1012',  '1020', '1021', '1022'],
            ['1100', '1101', '1102',   '1110', '1111', '1112',  '1120', '1121', '1122'],
            ['1200', '1201', '1202',   '1210', '1211', '1212',  '1220', '1221', '1222'],

            ['2000', '2001', '2002',   '2010', '2011', '2012',  '2020', '2021', '2022'],
            ['2100', '2101', '2102',   '2110', '2111', '2112',  '2120', '2121', '2122'],
            ['2200', '2201', '2202',   '2210', '2211', '2212',  '2220', '2221', '2222'],
        ]
        print("The initial tensor:")
        self.print_nice(self.daeg_str)
        self.daeg = self.to_numpy(self.daeg_str)


    def print_nice(self, daeg):
        """Formatted printout of the tensor."""

        # Loop over the rows.
        for i in range(9):
            # Empty row.
            if i != 0 and not i % 3:
                print(' |' + '-'*17 + '|' + '-'*17 + '|' + '-'*17)

            # Loop over the columns.
            line = ''
            for j in range(9):
                # Block separator.
                if not j % 3:
                    line = line + ' | '

                # The matrix element.
                if isinstance(daeg[i][j], str):
                    line = line + daeg[i][j] + " "
                else:
                    val = "%s" % int(daeg[i, j])
                    string = ['0', '0', '0', '0']
                    for k in range(1, len(val)+1):
                        string[-k] = val[-k]
                    string = '%s%s%s%s' % (string[0], string[1], string[2], string[3])
                    line = line + string + " "

            print(line + '|')
        print('')


    def string_transpose(self, index1, index2):
        """Manually transpose self.daeg_str using the 2 given indices."""

        # Initialise the matrix.
        daegT = []

        # The string indices.
        indices = list(range(4))
        temp = indices[index1-1]
        indices[index1-1] = indices[index2-1]
        indices[index2-1] = temp

        # Loop over the elements.
        for i in range(9):
            daegT.append([])
            for j in range(9):
                elem = self.daeg_str[i][j]
                daegT[-1].append('%s%s%s%s' % (elem[indices[0]], elem[indices[1]], elem[indices[2]], elem[indices[3]]))

        # Return.
        return daegT


    def to_numpy(self, tensor):
        """Convert the string version of the tensor into a numpy version."""

        # Initialise.
        new = zeros((9, 9), float64)

        # Loop over the elements.
        for i in range(9):
            for j in range(9):
                new[i, j] = float(tensor[i][j])

        # Return the tensor.
        return new


    def test_kron_prod(self):
        """Test the Kronecker product function kron_prod()."""

        # The 3D, rank-2 matrices.
        R1 = array([[1, 4, 5], [-4, 2, 6], [-5, -6, 3]], float64)
        R2 = array([[0, 1, 0], [0, 0, 0], [0, 0, 0]], float64)

        # The Kronecker product.
        C = kron_prod(R1, R2)

        # The real Kronecker product!
        D = array([
            [ 0,  1,  0,  0,  4,  0,  0,  5,  0],
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
            [ 0, -4,  0,  0,  2,  0,  0,  6,  0],
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
            [ 0, -5,  0,  0, -6,  0,  0,  3,  0],
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0]], float64)

        # Print outs.
        print("R1:\n%s" % R1)
        print("R2:\n%s" % R2)
        print("C:\n%s" % C)
        print("D:\n%s" % D)

        # Checks.
        self.assertEqual(C.shape, (9, 9))
        for i in range(9):
            for j in range(9):
                self.assertEqual(C[i, j], D[i, j])


    def test_transpose_12(self):
        """Check the 1,2 transpose of a rank-4, 3D tensor."""

        # Manually create the string rep of the transpose.
        daegT = self.string_transpose(1, 2)
        print("The real 1,2 transpose:")
        self.print_nice(daegT)

        # Convert to numpy.
        daegT = self.to_numpy(daegT)

        # Check.
        print("The numerical 1,2 transpose:")
        transpose_12(self.daeg)
        self.print_nice(self.daeg)
        for i in range(9):
            for j in range(9):
                print("i = %2s, j = %2s, daeg[i,j] = %s" % (i, j, daegT[i, j]))
                self.assertEqual(self.daeg[i, j], daegT[i, j])


    def test_transpose_13(self):
        """Check the 1,3 transpose of a rank-4, 3D tensor."""

        # Manually create the string rep of the transpose.
        daegT = self.string_transpose(1, 3)
        print("The real 1,3 transpose:")
        self.print_nice(daegT)

        # Convert to numpy.
        daegT = self.to_numpy(daegT)

        # Check.
        print("The numerical 1,3 transpose:")
        transpose_13(self.daeg)
        self.print_nice(self.daeg)
        for i in range(9):
            for j in range(9):
                print("i = %2s, j = %2s, daeg[i,j] = %s" % (i, j, daegT[i, j]))
                self.assertEqual(self.daeg[i, j], daegT[i, j])


    def test_transpose_14(self):
        """Check the 1,4 transpose of a rank-4, 3D tensor."""

        # Manually create the string rep of the transpose.
        daegT = self.string_transpose(1, 4)
        print("The real 1,4 transpose:")
        self.print_nice(daegT)

        # Convert to numpy.
        daegT = self.to_numpy(daegT)

        # Check.
        print("The numerical 1,4 transpose:")
        transpose_14(self.daeg)
        self.print_nice(self.daeg)
        for i in range(9):
            for j in range(9):
                print("i = %2s, j = %2s, daeg[i,j] = %s" % (i, j, daegT[i, j]))
                self.assertEqual(self.daeg[i, j], daegT[i, j])


    def test_transpose_23(self):
        """Check the 2,3 transpose of a rank-4, 3D tensor."""

        # Manually create the string rep of the transpose.
        daegT = self.string_transpose(2, 3)
        print("The real 2,3 transpose:")
        self.print_nice(daegT)

        # Convert to numpy.
        daegT = self.to_numpy(daegT)

        # Check.
        print("The numerical 2,3 transpose:")
        transpose_23(self.daeg)
        self.print_nice(self.daeg)
        for i in range(9):
            for j in range(9):
                print("i = %2s, j = %2s, daeg[i,j] = %s" % (i, j, daegT[i, j]))
                self.assertEqual(self.daeg[i, j], daegT[i, j])


    def test_transpose_24(self):
        """Check the 2,4 transpose of a rank-4, 3D tensor."""

        # Manually create the string rep of the transpose.
        daegT = self.string_transpose(2, 4)
        print("The real 2,4 transpose:")
        self.print_nice(daegT)

        # Convert to numpy.
        daegT = self.to_numpy(daegT)

        # Check.
        print("The numerical 2,4 transpose:")
        transpose_24(self.daeg)
        self.print_nice(self.daeg)
        for i in range(9):
            for j in range(9):
                print("i = %2s, j = %2s, daeg[i,j] = %s" % (i, j, daegT[i, j]))
                self.assertEqual(self.daeg[i, j], daegT[i, j])


    def test_transpose_34(self):
        """Check the 3,4 transpose of a rank-4, 3D tensor."""

        # Manually create the string rep of the transpose.
        daegT = self.string_transpose(3, 4)
        print("The real 3,4 transpose:")
        self.print_nice(daegT)

        # Convert to numpy.
        daegT = self.to_numpy(daegT)

        # Check.
        print("The numerical 3,4 transpose:")
        transpose_34(self.daeg)
        self.print_nice(self.daeg)
        for i in range(9):
            for j in range(9):
                print("i = %2s, j = %2s, daeg[i,j] = %s" % (i, j, daegT[i, j]))
                self.assertEqual(self.daeg[i, j], daegT[i, j])


    def test_transpose_reversions(self):
        """Check that the transposes revert back to the original matrix."""

        # Make a copy of the frame order matrix.
        daeg_orig = self.to_numpy(self.daeg_str)

        # List of transpose functions.
        Tij = [transpose_12, transpose_13, transpose_14, transpose_23, transpose_24, transpose_34]

        # Check the transpose reversions.
        for transpose in Tij:
            # Transpose twice.
            transpose(self.daeg)
            transpose(self.daeg)

            # Check.
            for i in range(9):
                for j in range(9):
                    print("i = %2s, j = %2s, daeg[i,j] = %s" % (i, j, daeg_orig[i, j]))
                    self.assertEqual(self.daeg[i, j], daeg_orig[i, j])
