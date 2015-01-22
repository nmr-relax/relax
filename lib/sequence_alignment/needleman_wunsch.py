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

# relax module imports.
from lib.errors import RelaxError, RelaxFault


# Default scores.
SCORE_MATCH = 1
SCORE_MISMATCH = -1
SCORE_GAP_PENALTY = 1
SCORES = zeros(3, int16)

# Indices.
TRACEBACK_DIAG = 0
TRACEBACK_TOP = 1
TRACEBACK_LEFT = 2


def needleman_wunsch_align(sequence1, sequence2, sub_matrix=None, sub_seq=None, gap_open_penalty=SCORE_GAP_PENALTY, gap_extend_penalty=1.0, end_gap_open_penalty=0.0, end_gap_extend_penalty=0.0):
    """Align two sequences using the Needleman-Wunsch algorithm using the EMBOSS logic for extensions.

    This is implemented as described in the U{Wikipedia article on the Needleman-Wunsch algorithm <https://en.wikipedia.org/wiki/Needleman%E2%80%93Wunsch_algorithm>}.  The algorithm has been modified to match that of U{EMBOSS<http://emboss.sourceforge.net/>} to allow for gap opening and extension penalties, as well as end penalties.


    @param sequence1:                   The first sequence.
    @type sequence1:                    str
    @param sequence2:                   The second sequence.
    @type sequence2:                    str
    @keyword sub_matrix:                The substitution matrix to use to determine the penalties.
    @type sub_matrix:                   numpy rank-2 int array
    @keyword sub_seq:                   The one letter code sequence corresponding to the substitution matrix indices.
    @type sub_seq:                      str
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

    # The sequence lengths.
    M = len(sequence1)
    N = len(sequence2)

    # Sanity check.
    for i in range(M):
        if sequence1[i] not in sub_seq:
            raise RelaxError("The residue '%s' from the first sequence cannot be found in the substitution matrix residues '%s'." % (sequence1[i], sub_seq))
    for j in range(N):
        if sequence2[j] not in sub_seq:
            raise RelaxError("The residue '%s' from the second sequence cannot be found in the substitution matrix residues '%s'." % (sequence2[j], sub_seq))

    # Calculate the scoring and traceback matrices.
    matrix, traceback_matrix = needleman_wunsch_matrix(sequence1, sequence2, sub_matrix=sub_matrix, sub_seq=sub_seq, gap_open_penalty=gap_open_penalty, gap_extend_penalty=gap_extend_penalty, end_gap_open_penalty=end_gap_open_penalty, end_gap_extend_penalty=end_gap_extend_penalty)

    # Generate the alignment.
    i = M - 1
    j = N - 1
    alignment1 = ""
    alignment2 = ""
    while 1:
        # Top.
        if j < 0 or traceback_matrix[i, j] == TRACEBACK_TOP:
            alignment1 += sequence1[i]
            alignment2 += '-'
            i -= 1

        # Left.
        elif i < 0 or traceback_matrix[i, j] == TRACEBACK_LEFT:
            alignment1 += '-'
            alignment2 += sequence2[j]
            j -= 1

        # Diagonal.
        elif traceback_matrix[i, j] == TRACEBACK_DIAG:
            alignment1 += sequence1[i]
            alignment2 += sequence2[j]
            i -= 1
            j -= 1

        # Unknown behaviour.
        else:
            raise RelaxFault

        # Termination.
        if i < 0 and j < 0:
            break

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


def needleman_wunsch_matrix(sequence1, sequence2, sub_matrix=None, sub_seq=None, gap_open_penalty=SCORE_GAP_PENALTY, gap_extend_penalty=1.0, end_gap_open_penalty=0.0, end_gap_extend_penalty=0.0, epsilon=1e-7):
    """Construct the Needleman-Wunsch matrix for the given two sequences using the EMBOSS logic.

    The algorithm has been modified to match that of U{EMBOSS<http://emboss.sourceforge.net/>} to allow for gap opening and extension penalties, as well as end penalties.


    @param sequence1:                   The first sequence.
    @type sequence1:                    str
    @param sequence2:                   The second sequence.
    @type sequence2:                    str
    @keyword sub_matrix:                The substitution matrix to use to determine the penalties.
    @type sub_matrix:                   numpy rank-2 int16 array
    @keyword sub_seq:                   The one letter code sequence corresponding to the substitution matrix indices.
    @type sub_seq:                      str
    @keyword gap_open_penalty:          The penalty for introducing gaps, as a positive number.
    @type gap_open_penalty:             float
    @keyword gap_extend_penalty:        The penalty for extending a gap, as a positive number.
    @type gap_extend_penalty:           float
    @keyword end_gap_open_penalty:      The optional penalty for opening a gap at the end of a sequence.
    @type end_gap_open_penalty:         float
    @keyword end_gap_extend_penalty:    The optional penalty for extending a gap at the end of a sequence.
    @type end_gap_extend_penalty:       float
    @keyword epsilon:                   A value close to zero to determine if two numbers are the same, within this precision.
    @type epsilon:                      float
    @return:                            The Needleman-Wunsch matrix and traceback matrix.
    @rtype:                             numpy rank-2 float32 array, numpy rank-2 int16 array
    """

    # Initial scoring matrix.
    M = len(sequence1)
    N = len(sequence2)
    matrix = zeros((M, N), float32)

    # Initial gap matrices.
    gap_matrix_vert = zeros((M, N), float32)
    gap_matrix_hori = zeros((M, N), float32)

    # Initial traceback matrix.
    traceback_matrix = zeros((M, N), int16)

    # Set up position [0, 0].
    matrix[0, 0] = sub_matrix[sub_seq.index(sequence1[0]), sub_seq.index(sequence2[0])]
    gap_matrix_vert[0, 0] = -gap_open_penalty
    gap_matrix_hori[0, 0] = -gap_open_penalty

    # Set up the first column.
    for i in range(1, M):
        # Substitution scores from the matrix.
        matrix[i, 0] = sub_matrix[sub_seq.index(sequence1[i]), sub_seq.index(sequence2[0])]

        # Gap scores.
        score_gap_open = matrix[i-1, 0] - gap_open_penalty
        score_gap_extend = gap_matrix_hori[i-1, 0] - gap_extend_penalty

        # Update the vertical gap matrix.
        if i < M-1:
            gap_matrix_vert[i, 0] = -gap_open_penalty

        # Update the horizontal gap matrix.
        gap_matrix_hori[i, 0] = max(score_gap_open, score_gap_extend)

    # Set up the first row.
    for j in range(1, N):
        # Substitution scores from the matrix.
        matrix[0, j] = sub_matrix[sub_seq.index(sequence1[0]), sub_seq.index(sequence2[j])]

        # Gap scores.
        score_gap_open = matrix[0, j-1] - gap_open_penalty
        score_gap_extend = gap_matrix_vert[0, j-1] - gap_extend_penalty

        # Update the vertical gap matrix.
        gap_matrix_vert[0, j] = max(score_gap_open, score_gap_extend)

        # Update the horizontal gap matrix.
        if j < N-1:
            gap_matrix_hori[0, j] = -gap_open_penalty

    # Fill in the rest of the matrix.
    for j in range(1, N):
        for i in range(1, M):
            # Substitution scores from the matrix.
            sub_score = sub_matrix[sub_seq.index(sequence1[i]), sub_seq.index(sequence2[j])]

            # The diagonal score.
            SCORES[0] = matrix[i-1, j-1]

            # The top score.
            SCORES[1] = gap_matrix_vert[i-1, j-1]

            # The left score.
            SCORES[2] = gap_matrix_hori[i-1, j-1]

            # Store the score.
            matrix[i, j] = SCORES.max() + sub_score

            # Horizontal gap scores.
            if j == N-1:
                score_gap_open = matrix[i-1, j] - end_gap_open_penalty
                score_gap_extend = gap_matrix_hori[i-1, j] - end_gap_extend_penalty
            else:
                score_gap_open = max(matrix[i-1, j], gap_matrix_vert[i-1, j]) - gap_open_penalty
                score_gap_extend = gap_matrix_hori[i-1, j] - gap_extend_penalty
            gap_matrix_hori[i, j] = max(score_gap_open, score_gap_extend)

            # Vertical gap scores.
            if i == M-1:
                score_gap_open = matrix[i, j-1] - end_gap_open_penalty
                score_gap_extend = gap_matrix_vert[i, j-1] - end_gap_extend_penalty
            else:
                score_gap_open = max(matrix[i, j-1], gap_matrix_hori[i, j-1]) - gap_open_penalty
                score_gap_extend = gap_matrix_vert[i, j-1] - gap_extend_penalty
            gap_matrix_vert[i, j] = max(score_gap_open, score_gap_extend)

    # Determine the best traceback path.
    j = N - 1
    i = M - 1
    last_move = 0
    while j >= 0 and i >= 0:
        # The current indices.
        curr_i = i
        curr_j = j

        # Choose the correct gap extension penalties.
        left_gap_extend_penalty = gap_extend_penalty
        top_gap_extend_penalty = gap_extend_penalty
        if i == 0 or i == M-1:
            left_gap_extend_penalty = end_gap_extend_penalty
        if j == 0 or j == N-1:
            top_gap_extend_penalty = end_gap_extend_penalty

        # Extending the gap to the left.
        if last_move == TRACEBACK_LEFT and abs(left_gap_extend_penalty - (gap_matrix_vert[i, j] - gap_matrix_vert[i, j+1])) < epsilon:
            traceback_matrix[i, j] = TRACEBACK_LEFT
            j -= 1

        # Extending the gap to the top.
        elif last_move== TRACEBACK_TOP and abs(top_gap_extend_penalty - (gap_matrix_hori[i, j] - gap_matrix_hori[i+1, j])) < epsilon:
            traceback_matrix[i, j] = TRACEBACK_TOP
            i -= 1

        # Match.
        elif matrix[i, j] >= gap_matrix_vert[i, j] and matrix[i, j] >= gap_matrix_hori[i, j]:
            # Add another gap to the left.
            if last_move == TRACEBACK_LEFT and abs(matrix[i, j] - gap_matrix_vert[i, j]) < epsilon:
                traceback_matrix[i, j] = TRACEBACK_LEFT
                j -= 1

            # Add another gap to the top.
            elif last_move == TRACEBACK_TOP and abs(matrix[i, j] - gap_matrix_hori[i, j]) < epsilon:
                traceback_matrix[i, j] = TRACEBACK_TOP
                i -= 1

            # Take the match.
            else:
                traceback_matrix[i, j] = 0
                i -= 1
                j -= 1

        # First gap to the left.
        elif gap_matrix_vert[i, j] >= gap_matrix_hori[i, j] and j >= 0:
            traceback_matrix[i, j] = TRACEBACK_LEFT
            j -= 1

        # First gap to the top.
        elif i >= 0:
            traceback_matrix[i, j] = TRACEBACK_TOP
            i -= 1

        # Store the last move.
        last_move = traceback_matrix[curr_i, curr_j]

    # Return the matrices.
    return matrix, traceback_matrix
