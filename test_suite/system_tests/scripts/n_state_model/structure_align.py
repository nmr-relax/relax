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
"""Script for testing the alignment of 3 structures."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Load the 3 PDB structures into 3 data pipes.
codes = ['1J7O', '1OSA', '1J7P']
for code in codes:
    # Create a data pipe.
    pipe.create(pipe_name=code, pipe_type='N-state')

    # Load the structure.
    structure.read_pdb('%s.pdb' % code, dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures')

# First align then superimpose the N-domains - aligning 1OSA onto 1J70 to act as a scaffold.
structure.sequence_alignment(pipes=['1J7O', '1OSA'], msa_algorithm='Central Star', pairwise_algorithm='NW70', matrix='BLOSUM62', gap_open_penalty=10.0, gap_extend_penalty=1.0, end_gap_open_penalty=0.0, end_gap_extend_penalty=0.0)
structure.superimpose(pipes=['1J7O', '1OSA'], atom_id='@N,C,CA,O', method='fit to first')

# Then align then superimpose the C-domains - aligning 1J7P onto the 1OSA scaffold.
structure.sequence_alignment(pipes=['1OSA', '1J7P'], msa_algorithm='Central Star', pairwise_algorithm='NW70', matrix='BLOSUM62', gap_open_penalty=10.0, gap_extend_penalty=1.0, end_gap_open_penalty=0.0, end_gap_extend_penalty=0.0)
structure.superimpose(pipes=['1OSA', '1J7P'], atom_id='@N,C,CA,O', method='fit to first')

# Write out the result.
structure.write_pdb('devnull', force=True)
