# Script for catching bug #20674 (https://gna.org/bugs/index.php?20674).

# Python module imports.
from os import sep
import sys

# relax module imports.
from status import Status; status = Status()


# Create the data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='jw_mapping', pipe_type='jw')

# The data directory.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'consistency_testing'+sep+'bug_20674_ct_analysis_failure'

# Load the PDB file.
self._execute_uf(uf_name='structure.read_pdb', file='2QFK_MONOMERHabc5.pdb', dir=path, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None)

# Set up the 15N and 1H spins (both backbone and Trp indole sidechains).
self._execute_uf(uf_name='structure.load_spins', spin_id='@N', ave_pos=True)
self._execute_uf(uf_name='structure.load_spins', spin_id='@H', ave_pos=True)
self._execute_uf(uf_name='spin.isotope', isotope='15N', spin_id='@N')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H')

# Load the relaxation data.
self._execute_uf(uf_name='bruker.read', ri_id='r1_700', file='T1 dhp 700.txt', dir=path)
self._execute_uf(uf_name='bruker.read', ri_id='r2_700', file='T2 dhp 700.txt', dir=path)
self._execute_uf(uf_name='bruker.read', ri_id='noe_700', file='NOE dhp 700.txt', dir=path)

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='interatom.define', spin_id1='@N', spin_id2='@H', direct_bond=True)
self._execute_uf(uf_name='interatom.set_dist', spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)

# Define the chemical shift relaxation interaction.
self._execute_uf(uf_name='value.set', val=-172 * 1e-6, param='csa')

# Set the frequency.
self._execute_uf(uf_name='jw_mapping.set_frq', frq=700.17 * 1e6)

# Consistency tests.
self._execute_uf(uf_name='calc')

# Monte Carlo simulations.
self._execute_uf(uf_name='monte_carlo.setup', number=10)
self._execute_uf(uf_name='monte_carlo.create_data')
self._execute_uf(uf_name='calc')
self._execute_uf(uf_name='monte_carlo.error_analysis')

# Create grace files.
self._execute_uf(uf_name='grace.write', y_data_type='j0', file='devnull', force=True)
self._execute_uf(uf_name='grace.write', y_data_type='jwx', file='devnull', force=True)
self._execute_uf(uf_name='grace.write', y_data_type='jwh', file='devnull', force=True)

# Finish.
self._execute_uf(uf_name='results.write', file='devnull', force=True)
self._execute_uf(uf_name='state.save', state='devnull')
