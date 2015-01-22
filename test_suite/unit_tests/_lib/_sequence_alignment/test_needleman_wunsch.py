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
from lib.sequence_alignment.substitution_matrices import NUC_4_4, NUC_4_4_SEQ, SIMILARITY_DNA, SIMILARITY_DNA_SEQ


class Test_needleman_wunsch(TestCase):
    """Unit tests for the lib.sequence_alignment.needleman_wunsch relax module."""

    def test_needleman_wunsch_align_DNA(self):
        """Test the Needleman-Wunsch sequence alignment for two DNA sequences."""

        # The sequences.
        seq1 = 'GCATTACT'
        seq2 = 'GATTACT'
        print("\nIn:")
        print(seq1)
        print(seq2)

        # Perform the alignment. 
        align1, align2, gaps = needleman_wunsch_align(seq1, seq2, sub_matrix=SIMILARITY_DNA, sub_seq=SIMILARITY_DNA_SEQ, gap_open_penalty=1, gap_extend_penalty=1)
        print("\nOut:")
        print(align1)
        print(align2)
        print(gaps)
        print("\n")

        # Check the alignment.
        self.assertEqual(align1, 'GCATTACT')
        self.assertEqual(align2, 'G-ATTACT')

        # The gap matrix.
        real_gaps = [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0]
        ]
        for i in range(2):
            for j in range(8):
                self.assertEqual(gaps[i, j], real_gaps[i][j])


    def test_needleman_wunsch_align_NUC_4_4(self):
        """Test the Needleman-Wunsch sequence alignment for two DNA sequences using the NUC 4.4 matrix.

        From online servers, the results with a gap open penalty of 5 and gap extend of 1 should be::

            https://www.ebi.ac.uk/Tools/psa/emboss_needle/
            EMBOSS_001         1 GAAAAAAT      8
                                 |    |||
            EMBOSS_001         1 G----AAT      4
        """

        # The sequences.
        seq1 = 'GAAAAAAT'
        seq2 = 'GAAT'
        print("\nIn:")
        print(seq1)
        print(seq2)

        # Perform the alignment. 
        align1, align2, gaps = needleman_wunsch_align(seq1, seq2, sub_matrix=NUC_4_4, sub_seq=NUC_4_4_SEQ, gap_open_penalty=5, gap_extend_penalty=1)
        print("\nOut:")
        print(align1)
        print(align2)
        print(gaps)
        print("\n")

        # Check the alignment.
        self.assertEqual(align1, 'GAAAAAAT')
        self.assertEqual(align2, 'G----AAT')

        # The gap matrix.
        real_gaps = [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 0, 0, 0]
        ]
        for i in range(2):
            for j in range(8):
                self.assertEqual(gaps[i, j], real_gaps[i][j])


    def test_needleman_wunsch_align_NUC_4_4b(self):
        """Test the Needleman-Wunsch sequence alignment for two DNA sequences using the NUC 4.4 matrix.

        From online servers, the results with a gap open penalty of 5 and gap extend of 1 should be::

            https://www.ebi.ac.uk/Tools/psa/emboss_needle/
            EMBOSS_001         1 GACAGAAT-      8
                                     |||| 
            EMBOSS_001         1 ----GAATA      5
        """

        # The sequences.
        seq1 = 'GACAGAAT'
        seq2 = 'GAATA'
        print("\nIn:")
        print(seq1)
        print(seq2)

        # Perform the alignment. 
        align1, align2, gaps = needleman_wunsch_align(seq1, seq2, sub_matrix=NUC_4_4, sub_seq=NUC_4_4_SEQ, gap_open_penalty=5, gap_extend_penalty=1)
        print("\nOut:")
        print(align1)
        print(align2)
        print(gaps)
        print("\n")

        # Check the alignment.
        self.assertEqual(align1, 'GACAGAAT-')
        self.assertEqual(align2, '----GAATA')

        # The gap matrix.
        real_gaps = [
                [0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 0, 0, 0, 0, 0]
        ]
        for i in range(2):
            for j in range(8):
                self.assertEqual(gaps[i, j], real_gaps[i][j])
