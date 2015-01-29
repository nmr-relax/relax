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

# Module docstring.
"""Multiple sequence alignment (MSA) algorithms."""

# Python module imports.
from numpy import int16, zeros
import sys

# relax module imports.
from lib.errors import RelaxError
from lib.sequence_alignment.needleman_wunsch import needleman_wunsch_align
from lib.sequence_alignment.substitution_matrices import BLOSUM62, BLOSUM62_SEQ, PAM250, PAM250_SEQ


def central_star(sequences, algorithm='NW70', matrix='BLOSUM62', gap_open_penalty=1.0, gap_extend_penalty=1.0, end_gap_open_penalty=0.0, end_gap_extend_penalty=0.0):
    """Align multiple protein sequences to one reference by fusing multiple pairwise alignments.

    @param sequences:                   The list of residue sequences as one letter codes.
    @type sequences:                    list of str
    @keyword algorithm:                 The pairwise sequence alignment algorithm to use.
    @type algorithm:                    str
    @keyword matrix:                    The substitution matrix to use.
    @type matrix:                       str
    @keyword gap_open_penalty:          The penalty for introducing gaps, as a positive number.
    @type gap_open_penalty:             float
    @keyword gap_extend_penalty:        The penalty for extending a gap, as a positive number.
    @type gap_extend_penalty:           float
    @keyword end_gap_open_penalty:      The optional penalty for opening a gap at the end of a sequence.
    @type end_gap_open_penalty:         float
    @keyword end_gap_extend_penalty:    The optional penalty for extending a gap at the end of a sequence.
    @type end_gap_extend_penalty:       float
    @return:                            The two alignment strings and the gap matrix.
    @rtype:                             str, str, numpy rank-2 int array
    """

    # The pairwise alignments.
    N = len(sequences)
    align1_list = []
    align2_list = []
    gap_list = []
    for i in range(N):
        # Pairwise alignment.
        align1, align2, gaps = align_pairwise(reference_sequence, sequences[i], algorithm=algorithm, matrix=matrix, gap_open_penalty=gap_open_penalty, gap_extend_penalty=gap_extend_penalty, end_gap_open_penalty=end_gap_open_penalty, end_gap_extend_penalty=end_gap_extend_penalty)

        # Store the results.
        align1_list.append(align1)
        align2_list.append(align2)
        gap_list.append(gaps)

    # Convert all sequence strings to lists.
    ref_list = list(reference_sequence)
    seq_list = []
    for i in range(N):
        seq_list.append(list(sequences[i]))

    # Loop over the alignment elements.
    strings = []
    index = -1
    offsets = zeros(N, int16)
    while 1:
        # Increment the index.
        index += 1
        print "\nIndex %i" % index

        # Termination condition.
        term = True
        for i in range(N):
            if index + offsets[i] < len(gap_list[i][0]):
                term = False
            else:
                print "    At end in %i" % i
        if term:
            break

        # A gap in one of the references.
        gap = False
        for i in range(N):
            if index + offsets[i] >= len(gap_list[i][0]) or gap_list[i][0, index]:
                print "    Gap in %i" % i
                offsets[i] += 1
                gap = True
        print "    New offsets %s" % offsets

        # No reference gap.
        if not gap:
            print "    No ref gap."
            continue

        # Insert the gap into the reference list.
        print "    Inserting gap into ref list at %i" % index
        ref_list.insert(index, '-')

    for i in range(N):
        seq = ''.join(seq_list[i])
        strings.append(seq)

    ref = ''.join(ref_list)

    print ref_list
    print seq_list

    # Return the results.
    return [ref] + strings, gap_list
