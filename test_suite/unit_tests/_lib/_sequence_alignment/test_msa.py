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
from numpy import int16, zeros
from unittest import TestCase

# relax module imports.
from lib.sequence_alignment.msa import central_star


class Test_msa(TestCase):
    """Unit tests for the lib.sequence_alignment.msa relax module."""

    def test_central_star(self):
        """Test the central star multiple sequence alignment function lib.sequence_alignment.msa.central_star().

        This uses the sequences:

            - 'TEEQVDADGGT',
            - 'ADQLTEEQVDADGNGTIDFPEFLTMMARKM',
            - 'LTEEQMINEVDAGNGTIDFPEFLTMMAR'.

        The result should be::

            Pairwise protein alignment.
            Substitution matrix:           BLOSUM62
            Gap opening penalty:           5.0
            Gap extend penalty:            1.0
            
            Input sequence 1:              TEEQVDADGGT
            Input sequence 2:              ADQLTEEQVDADGNGTIDFPEFLTMMARKM
            
            Aligned sequence 1:            ----TEEQVDADG-GT--------------
            Aligned sequence 2:            ADQLTEEQVDADGNGTIDFPEFLTMMARKM
                                               ********* **              
            
            
            Pairwise protein alignment.
            Substitution matrix:           BLOSUM62
            Gap opening penalty:           5.0
            Gap extend penalty:            1.0
            
            Input sequence 1:              TEEQVDADGGT
            Input sequence 2:              LTEEQMINEVDAGNGTIDFPEFLTMMAR
            
            Aligned sequence 1:            -TEEQ----VDADGGT------------
            Aligned sequence 2:            LTEEQMINEVDAGNGTIDFPEFLTMMAR
                                            ****    ***  **            

            ----TEEQ----VDADG-GT--------------
            ADQLTEEQ----VDADGNGTIDFPEFLTMMARKM
            ---LTEEQMINEVDA-GNGTIDFPEFLTMMAR--
        """

        # The sequences.
        seq1 =     'TEEQVDADGGT'
        seq2 = 'ADQLTEEQVDADGNGTIDFPEFLTMMARKM'
        seq3 =    'LTEEQMINEVDAGNGTIDFPEFLTMMAR'
        print(seq1)
        print(seq2)
        print(seq3)

        # Perform the alignment.
        strings, gaps = central_star([seq1, seq2, seq3], matrix='BLOSUM62', gap_open_penalty=5.0, gap_extend_penalty=1.0)
        print(strings[0])
        print(strings[1])
        print(strings[2])
        print(gaps)

        # Check the alignment.
        self.assertEqual(strings[0], '----TEEQ----VDADG-GT--------------')
        self.assertEqual(strings[1], 'ADQLTEEQ----VDADGNGTIDFPEFLTMMARKM')
        self.assertEqual(strings[2], '---LTEEQMINEVDA-GNGTIDFPEFLTMMAR--')

        # The gap matrix.
        real_gaps = zeros((3, 34), int16)
        for i in (range(4) + range(8, 12) + [17] + range(20, 34)):
            real_gaps[0, i] = 1
        for i in range(8, 12):
            real_gaps[1, i] = 1
        for i in (range(3) + [15, 33, 34]):
            real_gaps[2, i] = 1
        for i in range(3):
            for j in range(34):
                self.assertEqual(gaps[i, j], real_gaps[i][j])
