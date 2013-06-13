# Script for catching bug #20683, the failure due to infinite values in the Bruker Dynamics Centre file (https://gna.org/bugs/?20683).

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Create the data pipe.
pipe.create('tm2', 'mf')

# The data path.
path = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'model_free' + sep + 'bug_20683_bdc_inf_values'

# Load the PDB file.
structure.read_pdb(file='2QFK_MONOMERHabc5.pdb', dir=path, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None)

# Set up the 15N and 1H spins (both backbone and Trp indole sidechains).
structure.load_spins('@N', ave_pos=True)
structure.load_spins('@H', ave_pos=True)
spin.isotope('15N', spin_id='@N')
spin.isotope('1H', spin_id='@H')

# Load the relaxation data.
bruker.read(ri_id='r1_700', file='T1 dhp 700.txt', dir=path)
bruker.read(ri_id='r2_700', file='T2 dhp 700.txt', dir=path)
bruker.read(ri_id='noe_700', file='NOE dhp 700.txt', dir=path)
bruker.read(ri_id='r1_500', file='T1 dhp 500.txt', dir=path)
bruker.read(ri_id='r2_500', file='T2 dhp 500.txt', dir=path)
bruker.read(ri_id='noe_500', file='NOE dhp 500.txt', dir=path)

# Define the magnetic dipole-dipole relaxation interaction.
interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)
interatom.unit_vectors()

# Define the CSA relaxation interaction.
value.set(-172 * 1e-6, 'csa')

# Select the model-free model.
model_free.select_model(model='tm2')

# Grid search.
grid_search(inc=4)

# Minimise.
minimise('newton')
