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
"""Functions for implementing the Needleman-Wunsch sequence alignment algorithm."""

# Python module imports.
from numpy import float32, int16, zeros

# Default scores.
SCORE_MATCH = 1
SCORE_MISMATCH = -1
SCORE_GAP_PENALTY = -1
SCORES = zeros(3, int16)

# Indices.
TRACEBACK_DIAG = 0
TRACEBACK_TOP = 1
TRACEBACK_LEFT = 2


def needleman_wunsch_align(sequence1, sequence2, sub_matrix=None, sub_seq=None, gap_penalty=SCORE_GAP_PENALTY):
    """Align two sequences using the Needleman-Wunsch algorithm.

    This is implemented as described in the U{Wikipedia article on the Needleman-Wunsch algorithm <https://en.wikipedia.org/wiki/Needleman%E2%80%93Wunsch_algorithm>}.


    @param sequence1:           The first sequence.
    @type sequence1:            str
    @param sequence2:           The second sequence.
    @type sequence2:            str
    @keyword sub_matrix:        The substitution matrix to use to determine the penalties.
    @type sub_matrix:           numpy rank-2 int array
    @keyword sub_seq:           The one letter code sequence corresponding to the substitution matrix indices.
    @type sub_seq:              str
    @keyword gap_penalty:       The penalty for introducing gaps, as a positive number.
    @type gap_penalty:          float
    @return:                    The two alignment strings and the gap matrix.
    @rtype:                     str, str, numpy rank-2 int array
    """

    # The sequence lengths.
    M = len(sequence1)
    N = len(sequence2)

    # Calculate the scoring and traceback matrices.
    matrix, traceback_matrix = needleman_wunsch_matrix(sequence1, sequence2, sub_matrix=sub_matrix, sub_seq=sub_seq, gap_penalty=gap_penalty)

    # Generate the alignment.
    i = M - 1
    j = N - 1
    alignment1 = ""
    alignment2 = ""
    while 1:
        # Termination.
        if i < 0 or j < 0:
            break

        # Diagonal.
        if traceback_matrix[i, j] == TRACEBACK_DIAG:
            alignment1 += sequence1[i]
            alignment2 += sequence2[j]
            i -= 1
            j -= 1

        # Top.
        elif traceback_matrix[i, j] == TRACEBACK_TOP:
            alignment1 += sequence1[i]
            alignment2 += '-'
            i -= 1

        # Left.
        elif traceback_matrix[i, j] == TRACEBACK_LEFT:
            alignment1 += '-'
            alignment2 += sequence2[j]
            j -= 1

    # Reverse the alignments.
    align1 = alignment1[::-1]
    align2 = alignment2[::-1]

    # Gap representation.
    gaps = zeros((2, len(align1)), int16)
    for l in range(len(align1)):
        if align1[l] == '-':
            gaps[0, l] = 1
        if align2[l] == '-':
            gaps[1, l] = 1

    # Return the alignments and gap matrix.
    return align1, align2, gaps


def needleman_wunsch_matrix(sequence1, sequence2, sub_matrix=None, sub_seq=None, gap_penalty=SCORE_GAP_PENALTY):
    """Construct the Needleman-Wunsch matrix for the given two sequences.

    @param sequence1:           The first sequence.
    @type sequence1:            str
    @param sequence2:           The second sequence.
    @type sequence2:            str
    @keyword sub_matrix:        The substitution matrix to use to determine the penalties.
    @type sub_matrix:           numpy rank-2 int16 array
    @keyword sub_seq:           The one letter code sequence corresponding to the substitution matrix indices.
    @type sub_seq:              str
    @keyword gap_penalty:       The penalty for introducing gaps, as a positive number.
    @type gap_penalty:          float
    @return:                    The Needleman-Wunsch matrix and traceback matrix.
    @rtype:                     numpy rank-2 float32 array, numpy rank-2 int16 array
    """

    # Initial scoring matrix.
    matrix = zeros((len(sequence1)+1, len(sequence2)+1), float32)
    for i in range(1, len(matrix)):
        matrix[i, 0] = -gap_penalty*i
    for j in range(1, len(matrix[0])):
        matrix[0, j] = -gap_penalty*j

    # Initial traceback matrix.
    traceback_matrix = zeros((len(sequence1), len(sequence2)), int16)

    # Calculate the scores.
    for i in range(1, len(matrix)):
        for j in range(1, len(matrix[0])):
            # Substitution scores when no matrix is provided.
            if sub_matrix == None:
                sub_score = SCORE_MISMATCH
                if sequence1[i-1] == sequence2[j-1]:
                    sub_score = SCORE_MATCH

            # Substitution scores from the matrix.
            else:
                sub_score = sub_matrix[sub_seq.index(sequence1[i-1]), sub_seq.index(sequence2[j-1])]

            # The diagonal score.
            SCORES[0] = matrix[i-1, j-1] + sub_score

            # The top score.
            SCORES[1] = matrix[i-1, j] - gap_penalty

            # The left score.
            SCORES[2] = matrix[i, j-1] - gap_penalty

            # Store the best score.
            matrix[i, j] = SCORES.max()

            # Update the traceback matrix.
            traceback_matrix[i-1, j-1] = SCORES.argmax()

    # Return the matrix.
    return matrix, traceback_matrix
