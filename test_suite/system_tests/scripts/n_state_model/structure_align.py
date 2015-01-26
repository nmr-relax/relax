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

# Backbone heavy atom align all structures.
structure.align(pipes=codes, atom_id='@N,C,CA,O', method='fit to first', matrix='BLOSUM62', gap_open_penalty=10.0, gap_extend_penalty=1.0, end_gap_open_penalty=0.0, end_gap_extend_penalty=0.0)

# Write out the result.
structure.write_pdb('devnull', force=True)
