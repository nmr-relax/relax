# Python module imports.
from os import sep

# relax imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Missing temp directory (allow this script to run outside of the system test framework).
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = 'temp_script'

# Create a data pipe.
pipe.create('pca test', 'N-state')

# Load the structures.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'pca'
structure.read_pdb('distribution.pdb', dir=path, read_mol=1, set_mol_name='CaM A')
structure.read_pdb('distribution.pdb', dir=path, read_mol=4, set_mol_name='CaM A', merge=True)

# Sequence alignment.
structure.sequence_alignment(msa_algorithm='residue number')

# PCA analysis.
structure.pca(dir=ds.tmpdir)

# Save the program state.
state.save(force=True, dir=ds.tmpdir)
