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
from unittest import TestCase

# relax module imports.
from lib.sequence_alignment.needleman_wunsch import needleman_wunsch_align


class Test_needleman_wunsch(TestCase):
    """Unit tests for the lib.sequence_alignment.needleman_wunsch relax module."""

    def test_needleman_wunsch_align_DNA(self):
        """Test the Needleman-Wunsch sequence alignment for two DNA sequences."""

        # The sequences.
        seq1 = 'GCATGCU'
        seq2 = 'GATTACA'
        print("\nIn:")
        print(seq1)
        print(seq2)

        # Perform the alignment. 
        align1, align2, gaps = needleman_wunsch_align(seq1, seq2)
        print("\nOut:")
        print(align1)
        print(align2)
        print(gaps)
        print("\n")

        # Check the alignment.
        self.assertEqual(align1, 'GCA-TGCU')
        self.assertEqual(align2, 'G-ATTACA')

        # The gap matrix.
        real_gaps = [
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0]
        ]
        for i in range(2):
            for j in range(8):
                self.assertEqual(gaps[i, j], real_gaps[i][j])
