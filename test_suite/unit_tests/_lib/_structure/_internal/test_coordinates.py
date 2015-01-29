###############################################################################
#                                                                             #
# Copyright (C) 2015 Edward d'Auvergne                                        #
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
from numpy import array, int16

# relax module imports.
from lib.structure.internal import coordinates
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_coordinates(UnitTestCase):
    """Unit tests for the functions of the 'lib.structure.internal.coordinates' module."""

    def test_common_residues(self):
        """Test the lib.structure.internal.coordinates.common_residues() function."""

        # The gap matrices.
        gap_matrices = [
            array([
                [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ], int16),
            array([
                [1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ], int16)
        ]
        seq1 =     'TEEQVDADGGT'
        seq2 = 'ADQLTEEQVDADGNGTIDFPEFLTMMARKM'
        seq3 =    'LTEEQMINEVDAGNGTIDFPEFLTMMAR'

        # Determine the common residues.
        skip, gapped_strings = coordinates.common_residues(gap_matrices=gap_matrices, one_letter_codes=[seq1, seq2, seq3], seq=True)

        # The expected skipping matrices.
        N = len(seq1)
        skip_real = [
            [0]*4 + [1]*4 + [0]*(N-8),
            [1]*4 + [0]*N + [1]*(len(seq2)-N-4),
            [1] + [0]*N + [1]*(len(seq3)-N-1)
        ]

        # The expected gapped strings.
        gapped_seq1 = '----TEEQ----VDA-G-GT----------------'
        gapped_seq2 = '----TEEQ----VDA-G-GT----------------'
        gapped_seq3 = '----TEEQMINEVDA-G-GT----------------'
        gapped_real = [gapped_seq1, gapped_seq2, gapped_seq3]

        # Checks.
        for i in range(3):
            print("Sequence %i" % (i+1))
            self.assertEqual(len(skip_real[i]), len(skip[i]))
            for j in range(len(skip_real[i])):
                self.assertEqual(skip_real[i][j], skip[i][j])
            #self.assertEqual(gapped_real[i], gapped_strings[i])
