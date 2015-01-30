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
from data_store.seq_align import Sequence_alignments


class Test_seq_align(TestCase):
    """Unit tests for the data.seq_align relax module."""


    def setUp(self):
        """Set 'self.seq_align' to an empty instance of the Sequence_alignments class."""

        self.seq_align = Sequence_alignments()


    def generate_ids(self, object_ids, models, molecules):
        """Generate the expected IDs."""

        # Generate the IDs.
        ids = []
        for i in range(len(object_ids)):
            ids.append("Object '%s'" % object_ids[i])
            if models[i] != None:
                ids[-1] += "; Model %i" % models[i]
            ids[-1] += "; Molecule '%s'" % molecules[i]

        # Return the IDs.
        return ids


    def return_align_data(self):
        """Return a data set for alignment testing."""

        # The data.
        object_ids = ['frame_order', 'ensemble', 'ensemble', 'ensemble', 'ensemble', 'ensemble', 'ensemble', 'ensemble']
        models = [None, 1, 1, 1, 1, 1, 1, 1]
        molecules = [
            'N-dom',
            'ensemble 4M A',
            'ensemble 4M B',
            'ensemble 4M C',
            'ensemble 4M D',
            'CaM-IQ A',
            'CaM-IQ B',
            'CaM-IQ C'
        ]
        sequences = [
            'LTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARK*****',
            '*DQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKMKDTDSEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTA*****',
            '*DQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKMKDTDSEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTA*****',
            '*DQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKMKDTDSEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTA*****',
            '*DQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKMKDTDSEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTA*****',
            '                                                                                                                           QLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKMKSEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMT*****',
            '                                                                                                                           LTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKMKDEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMT*****',
            '                                                                                                                           LTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMT*****',

            'TEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADG',
            'ADQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKM',
            'LTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMAR'
        ]
        strings = [
            '---LTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARK------------------------------------------------------------------------*****----------------------------------------------------------------------------',
            '*DQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARK----------------------------------------------------------------------------MKDTDSEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTA*****',
            '*DQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKMKDTDSEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTA*****----------------------------------------------------------------------------',
            '*DQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKMKDTDSEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTA*****----------------------------------------------------------------------------',
            '*DQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKMKDTDSEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTA*****----------------------------------------------------------------------------',
            '--QLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARK----MKSEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMT*****----------------------------------------------------------------------------',
            '---LTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARK----MKDEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMT*****----------------------------------------------------------------------------',
            '---LTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARK-------EEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMT*****----------------------------------------------------------------------------',
        ]
        gaps = []
        for i in range(len(strings)):
            gaps.append([])
            for j in range(len(strings[0])):
                if strings[i][j] == '-':
                    gaps[i].append(1)
                else:
                    gaps[i].append(0)
        msa_algorithm = 'Central Star'
        pairwise_algorithm = 'NW70'
        matrix = 'BLOSUM62'
        gap_open_penalty = 10.0
        gap_extend_penalty = 1.0
        end_gap_open_penalty = 0.0
        end_gap_extend_penalty = 0.0

        # Return the data.
        return object_ids, models, molecules, sequences, strings, gaps, msa_algorithm, pairwise_algorithm, matrix, gap_open_penalty, gap_extend_penalty, end_gap_open_penalty, end_gap_extend_penalty


    def test_alignment_addition(self):
        """Test the creation of a new sequence alignment object."""

        # The data.
        object_ids, models, molecules, sequences, strings, gaps, msa_algorithm, pairwise_algorithm, matrix, gap_open_penalty, gap_extend_penalty, end_gap_open_penalty, end_gap_extend_penalty = self.return_align_data()

        # Add the alignment.
        self.seq_align.add(object_ids=object_ids, models=models, molecules=molecules, sequences=sequences, strings=strings, gaps=gaps, msa_algorithm=msa_algorithm, pairwise_algorithm=pairwise_algorithm, matrix=matrix, gap_open_penalty=gap_open_penalty, gap_extend_penalty=gap_extend_penalty, end_gap_open_penalty=end_gap_open_penalty, end_gap_extend_penalty=end_gap_extend_penalty)

        # Generate the expected IDs.
        ids = self.generate_ids(object_ids, models, molecules)

        # Check the data.
        for i in range(8):
            print("Checking \"%s\"" % ids[i])
            self.assertEqual(self.seq_align[0].ids[i], ids[i])
            self.assertEqual(self.seq_align[0].object_ids[i], object_ids[i])
            self.assertEqual(self.seq_align[0].models[i], models[i])
            self.assertEqual(self.seq_align[0].molecules[i], molecules[i])
            self.assertEqual(self.seq_align[0].sequences[i], sequences[i])
            self.assertEqual(self.seq_align[0].strings[i], strings[i])
            self.assertEqual(self.seq_align[0].gaps[i], gaps[i])
            self.assertEqual(self.seq_align[0].msa_algorithm, msa_algorithm)
            self.assertEqual(self.seq_align[0].pairwise_algorithm, pairwise_algorithm)
            self.assertEqual(self.seq_align[0].matrix, matrix)
            self.assertEqual(self.seq_align[0].gap_open_penalty, gap_open_penalty)
            self.assertEqual(self.seq_align[0].gap_extend_penalty, gap_extend_penalty)
            self.assertEqual(self.seq_align[0].end_gap_open_penalty, end_gap_open_penalty)
            self.assertEqual(self.seq_align[0].end_gap_extend_penalty, end_gap_extend_penalty)


    def test_find_alignment(self):
        """Test the retrieval of pre-existing alignment."""

        # Execute the body of the test_alignment_addition() unit test to set up the object.
        self.test_alignment_addition()

        # The identifying data.
        object_ids, models, molecules, sequences, strings, gaps, msa_algorithm, pairwise_algorithm, matrix, gap_open_penalty, gap_extend_penalty, end_gap_open_penalty, end_gap_extend_penalty = self.return_align_data()

        # Retrieve the alignment.
        align = self.seq_align.find_alignment(object_ids=object_ids, models=models, molecules=molecules, sequences=sequences, msa_algorithm=msa_algorithm, pairwise_algorithm=pairwise_algorithm, matrix=matrix, gap_open_penalty=gap_open_penalty, gap_extend_penalty=gap_extend_penalty, end_gap_open_penalty=end_gap_open_penalty, end_gap_extend_penalty=end_gap_extend_penalty)

        # Check that something was returned.
        self.assertNotEqual(align, None)

        # Generate the expected IDs.
        ids = self.generate_ids(object_ids, models, molecules)

        # Check some of the data.
        for i in range(8):
            print("Checking \"%s\"" % ids[i])
            self.assertEqual(self.seq_align[0].object_ids[i], object_ids[i])
            self.assertEqual(self.seq_align[0].models[i], models[i])
            self.assertEqual(self.seq_align[0].molecules[i], molecules[i])


    def test_find_missing_alignment(self):
        """Test the retrieval of non-existent alignment."""

        # Execute the body of the test_alignment_addition() unit test to set up the object.
        self.test_alignment_addition()

        # The identifying data.
        object_ids, models, molecules, sequences, strings, gaps, msa_algorithm, pairwise_algorithm, matrix, gap_open_penalty, gap_extend_penalty, end_gap_open_penalty, end_gap_extend_penalty = self.return_align_data()

        # Change a gap penalty.
        gap_open_penalty = 0.5

        # Retrieve the alignment.
        align = self.seq_align.find_alignment(object_ids=object_ids, models=models, molecules=molecules, sequences=sequences, msa_algorithm=msa_algorithm, pairwise_algorithm=pairwise_algorithm, matrix=matrix, gap_open_penalty=gap_open_penalty, gap_extend_penalty=gap_extend_penalty, end_gap_open_penalty=end_gap_open_penalty, end_gap_extend_penalty=end_gap_extend_penalty)

        # Check that nothing was returned.
        self.assertEqual(align, None)
