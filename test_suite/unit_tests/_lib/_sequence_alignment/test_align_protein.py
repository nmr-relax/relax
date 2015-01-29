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
from lib.sequence_alignment.align_protein import align_multiple_from_pairwise, align_pairwise


class Test_align_protein(TestCase):
    """Unit tests for the lib.sequence_alignment.align_protein relax module."""

    def test_align_pairwise_PAM250(self):
        """Test the Needleman-Wunsch sequence alignment for two protein sequences using the PAM250 substitution matrix.

        This uses the sequences:

            - 'IHAAEEKDWKTAYSYbgFYEAFEGYdsidspkaitslkymllckimlntpedvqalvsgkla',
            - 'LHAADEKDFKTAFSYabiggapFYEAFEGYdsvdekvsaltalkymllckvmldlpdevnsllsakl'.

        From online servers, the results with a gap open penalty of 5 and gap extend of 0.5 should be::

            https://www.ebi.ac.uk/Tools/psa/emboss_needle/
            EMBOSS_001          IHAAEEKDWKTAYSYb--g---FYEAFEGYdsidspk--aitslkymllckimlntpedvqalvsgkla
                                :|||:|||.|||:||.  |   ||||||||||:|. |  |:|:||||||||:||:.|::|::|:|:|| 
            EMBOSS_001          LHAADEKDFKTAFSYabiggapFYEAFEGYdsvde-kvsaltalkymllckvmldlpdevnsllsakl-

            http://web.expasy.org/cgi-bin/sim/sim.pl?prot
            UserSeq1            IHAAEEKDWKTAYSYBG-----FYEAFEGYDSIDSPK--AITSLKYMLLCKIMLNTPEDVQALVSGKL
            UserSeq2            LHAADEKDFKTAFSYABIGGAPFYEAFEGYDSVDE-KVSALTALKYMLLCKVMLDLPDEVNSLLSAKL
                                 *** *** *** **       ********** *  *  * * ******** **  *  *  * * **
        """

        # The sequences.
        seq1 = 'IHAAEEKDWKTAYSYbgFYEAFEGYdsidspkaitslkymllckimlntpedvqalvsgkla'
        seq2 = 'LHAADEKDFKTAFSYabiggapFYEAFEGYdsvdekvsaltalkymllckvmldlpdevnsllsakl'
        print(seq1)
        print(seq2)

        # Perform the alignment.
        align1, align2, gaps = align_pairwise(seq1, seq2, matrix='PAM250', gap_open_penalty=5.0, gap_extend_penalty=0.5)
        print(align1)
        print(align2)
        print(gaps)

        # Check the alignment.
        self.assertEqual(align1, 'IHAAEEKDWKTAYSYB--G---FYEAFEGYDSIDSPK--AITSLKYMLLCKIMLNTPEDVQALVSGKLA')
        self.assertEqual(align2, 'LHAADEKDFKTAFSYABIGGAPFYEAFEGYDSVDE-KVSALTALKYMLLCKVMLDLPDEVNSLLSAKL-')

        # The gap matrix.
        real_gaps = zeros((2, 69), int16)
        real_gaps[0, 16] = 1
        real_gaps[0, 17] = 1
        real_gaps[0, 19] = 1
        real_gaps[0, 20] = 1
        real_gaps[0, 21] = 1
        real_gaps[0, 37] = 1
        real_gaps[0, 38] = 1
        real_gaps[1, 35] = 1
        real_gaps[1, 68] = 1
        for i in range(2):
            for j in range(68):
                self.assertEqual(gaps[i, j], real_gaps[i][j])
    def test_align_pairwise(self):
        """Test the Needleman-Wunsch sequence alignment for two protein sequences.

        This uses the sequences:

            - 'IHAAEEKDWKTAYSYbgFYEAFEGYdsidspkaitslkymllckimlntpedvqalvsgkla',
            - 'LHAADEKDFKTAFSYabiggapFYEAFEGYdsvdekvsaltalkymllckvmldlpdevnsllsakl'.

        From online servers, the results with a gap open penalty of 5 and gap extend of 1 should be::

            https://www.ebi.ac.uk/Tools/psa/emboss_needle/
            EMBOSS_001           IHAAEEKDWKTAYSY-B-G---FYEAFEGYDSIDSP-KAITSLKYMLLCKIMLNTPEDVQALVSGKLA
                                 :|||:|||:|||:|| | |   ||||||||||:|.. .|:|:||||||||:||:.|::|.:|:|.||
            EMBOSS_001           LHAADEKDFKTAFSYABIGGAPFYEAFEGYDSVDEKVSALTALKYMLLCKVMLDLPDEVNSLLSAKL-

            http://web.expasy.org/cgi-bin/sim/sim.pl?prot
            UserSeq1             IHAAEEKDWKTAYSY-B-G---FYEAFEGYDSIDSP-KAITSLKYMLLCKIMLNTPEDVQALVSGKL
            UserSeq2             LHAADEKDFKTAFSYABIGGAPFYEAFEGYDSVDEKVSALTALKYMLLCKVMLDLPDEVNSLLSAKL
                                  *** *** *** ** * *   ********** *    * * ******** **  *  *  * * **
        """

        # The sequences.
        seq1 = 'IHAAEEKDWKTAYSYbgFYEAFEGYdsidspkaitslkymllckimlntpedvqalvsgkla'
        seq2 = 'LHAADEKDFKTAFSYabiggapFYEAFEGYdsvdekvsaltalkymllckvmldlpdevnsllsakl'
        print(seq1)
        print(seq2)

        # Perform the alignment.
        align1, align2, gaps = align_pairwise(seq1, seq2, matrix='BLOSUM62', gap_open_penalty=5.0, gap_extend_penalty=1.0)
        print(align1)
        print(align2)
        print(gaps)

        # Check the alignment.
        self.assertEqual(align1, 'IHAAEEKDWKTAYSY-B-G---FYEAFEGYDSIDSP-KAITSLKYMLLCKIMLNTPEDVQALVSGKLA')
        self.assertEqual(align2, 'LHAADEKDFKTAFSYABIGGAPFYEAFEGYDSVDEKVSALTALKYMLLCKVMLDLPDEVNSLLSAKL-')

        # The gap matrix.
        real_gaps = zeros((2, 68), int16)
        real_gaps[0, 15] = 1
        real_gaps[0, 17] = 1
        real_gaps[0, 19] = 1
        real_gaps[0, 20] = 1
        real_gaps[0, 21] = 1
        real_gaps[0, 36] = 1
        real_gaps[1, 67] = 1
        for i in range(2):
            for j in range(68):
                self.assertEqual(gaps[i, j], real_gaps[i][j])


    def test_align_pairwise_PAM250(self):
        """Test the Needleman-Wunsch sequence alignment for two protein sequences using the PAM250 substitution matrix.

        This uses the sequences:

            - 'IHAAEEKDWKTAYSYbgFYEAFEGYdsidspkaitslkymllckimlntpedvqalvsgkla',
            - 'LHAADEKDFKTAFSYabiggapFYEAFEGYdsvdekvsaltalkymllckvmldlpdevnsllsakl'.

        From online servers, the results with a gap open penalty of 5 and gap extend of 0.5 should be::

            https://www.ebi.ac.uk/Tools/psa/emboss_needle/
            EMBOSS_001          IHAAEEKDWKTAYSYb--g---FYEAFEGYdsidspk--aitslkymllckimlntpedvqalvsgkla
                                :|||:|||.|||:||.  |   ||||||||||:|. |  |:|:||||||||:||:.|::|::|:|:|| 
            EMBOSS_001          LHAADEKDFKTAFSYabiggapFYEAFEGYdsvde-kvsaltalkymllckvmldlpdevnsllsakl-

            http://web.expasy.org/cgi-bin/sim/sim.pl?prot
            UserSeq1            IHAAEEKDWKTAYSYBG-----FYEAFEGYDSIDSPK--AITSLKYMLLCKIMLNTPEDVQALVSGKL
            UserSeq2            LHAADEKDFKTAFSYABIGGAPFYEAFEGYDSVDE-KVSALTALKYMLLCKVMLDLPDEVNSLLSAKL
                                 *** *** *** **       ********** *  *  * * ******** **  *  *  * * **
        """

        # The sequences.
        seq1 = 'IHAAEEKDWKTAYSYbgFYEAFEGYdsidspkaitslkymllckimlntpedvqalvsgkla'
        seq2 = 'LHAADEKDFKTAFSYabiggapFYEAFEGYdsvdekvsaltalkymllckvmldlpdevnsllsakl'
        print(seq1)
        print(seq2)

        # Perform the alignment.
        align1, align2, gaps = align_pairwise(seq1, seq2, matrix='PAM250', gap_open_penalty=5.0, gap_extend_penalty=0.5)
        print(align1)
        print(align2)
        print(gaps)

        # Check the alignment.
        self.assertEqual(align1, 'IHAAEEKDWKTAYSYB--G---FYEAFEGYDSIDSPK--AITSLKYMLLCKIMLNTPEDVQALVSGKLA')
        self.assertEqual(align2, 'LHAADEKDFKTAFSYABIGGAPFYEAFEGYDSVDE-KVSALTALKYMLLCKVMLDLPDEVNSLLSAKL-')

        # The gap matrix.
        real_gaps = zeros((2, 69), int16)
        real_gaps[0, 16] = 1
        real_gaps[0, 17] = 1
        real_gaps[0, 19] = 1
        real_gaps[0, 20] = 1
        real_gaps[0, 21] = 1
        real_gaps[0, 37] = 1
        real_gaps[0, 38] = 1
        real_gaps[1, 35] = 1
        real_gaps[1, 68] = 1
        for i in range(2):
            for j in range(68):
                self.assertEqual(gaps[i, j], real_gaps[i][j])
