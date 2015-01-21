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
from numpy import int16, zeros

# Default scores.
SCORE_MATCH = 1
SCORE_MISMATCH = -1
SCORE_GAP_PENALTY = -1
SCORES = zeros(3, int16)

# Indices.
TRACEBACK_DIAG = 0
TRACEBACK_TOP = 1
TRACEBACK_LEFT = 2


def needleman_wunsch_align(sequence1, sequence2):
    """Align two sequences using the Needleman-Wunsch algorithm.

    This is implemented as described in the U{Wikipedia article on the Needleman-Wunsch algorithm <https://en.wikipedia.org/wiki/Needleman%E2%80%93Wunsch_algorithm>}.


    @param sequence1:   The first sequence.
    @type sequence1:    str
    @param sequence2:   The second sequence.
    @type sequence2:    str
    @return:            The two alignment strings and the gap matrix.
    @rtype:             str, str, numpy rank-2 int array
    """

    # The sequence lengths.
    M = len(sequence1)
    N = len(sequence2)

    # Calculate the scoring and traceback matrices.
    matrix, traceback_matrix = needleman_wunsch_matrix(sequence1, sequence2)

    # Generate the alignment.
    i = M - 1
    j = N - 1
    alignment1 = ""
    alignment2 = ""
    while i >= 0 or j >= 0:
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


def needleman_wunsch_matrix(sequence1, sequence2):
    """Construct the Needleman-Wunsch matrix for the given two sequences.

    @param sequence1:   The first sequence.
    @type sequence1:    str
    @param sequence2:   The second sequence.
    @type sequence2:    str
    @return:            The Needleman-Wunsch matrix and traceback matrix.
    @rtype:             numpy rank-2 int array, numpy rank-2 int array
    """

    # Initial scoring matrix.
    matrix = zeros((len(sequence1)+1, len(sequence2)+1), int16)
    for i in range(len(matrix)):
        matrix[i, 0] = -i
    for j in range(len(matrix[0])):
        matrix[0, j] = -j

    # Initial traceback matrix.
    traceback_matrix = zeros((len(sequence1), len(sequence2)), int16)

    # Calculate the scores.
    for i in range(1, len(matrix)):
        for j in range(1, len(matrix[0])):
            # Substitution scores.
            sub_score = SCORE_MISMATCH
            if sequence1[i-1] == sequence2[j-1]:
                sub_score = SCORE_MATCH

            # The diagonal score.
            SCORES[0] = matrix[i-1, j-1] + sub_score

            # The top score.
            SCORES[1] = matrix[i-1, j] + SCORE_GAP_PENALTY

            # The left score.
            SCORES[2] = matrix[i, j-1] + SCORE_GAP_PENALTY

            # Store the best score.
            matrix[i, j] = SCORES.max()

            # Update the traceback matrix.
            traceback_matrix[i-1, j-1] = SCORES.argmax()

    # Return the matrix.
    return matrix, traceback_matrix
