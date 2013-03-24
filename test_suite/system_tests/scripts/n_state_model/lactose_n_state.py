# Script for determining populations for lactose conformations using RDCs and PCSs.

# Python module imports.
from os import sep
import sys

# relax imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from specific_analyses.setup import n_state_model_obj
from status import Status; status = Status()


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'

# Create the data pipe.
self._execute_uf('lactose', 'N-state', uf_name='pipe.create')

# The population model for free operation of this script.
if not hasattr(ds, 'model'):
    ds.model = 'population'

# Load the structures.
NUM_STR = 4
for i in range(NUM_STR):
    self._execute_uf(uf_name='structure.read_pdb', file='lactose_MCMM4_S1_'+repr(i+1), dir=str_path, set_model_num=i+1, set_mol_name='lactose_MCMM4_S1')

# Set up the 13C and 1H spins information.
self._execute_uf(uf_name='structure.load_spins', spin_id=':UNK@C*', ave_pos=False)
self._execute_uf(uf_name='structure.load_spins', spin_id=':UNK@H*', ave_pos=False)
self._execute_uf(uf_name='spin.isotope', isotope='13C', spin_id='@C*')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H*')

# Deselect the CH2 protons (the rotation of these doesn't work in the model, but the carbon doesn't move).
self._execute_uf(uf_name='deselect.spin', spin_id=':UNK@H6')
self._execute_uf(uf_name='deselect.spin', spin_id=':UNK@H7')
self._execute_uf(uf_name='deselect.spin', spin_id=':UNK@H17')
self._execute_uf(uf_name='deselect.spin', spin_id=':UNK@H18')

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='dipole_pair.define', spin_id1='@C*', spin_id2='@H*', direct_bond=True)
self._execute_uf(uf_name='dipole_pair.set_dist', spin_id1='@C*', spin_id2='@H*', ave_dist=1.10 * 1e-10)
self._execute_uf(uf_name='dipole_pair.unit_vectors', ave=False)

# Deselect the CH2 bonds.
self._execute_uf(uf_name='deselect.interatom', spin_id1=':UNK@C6', spin_id2=':UNK@H6')
self._execute_uf(uf_name='deselect.interatom', spin_id1=':UNK@C6', spin_id2=':UNK@H7')
self._execute_uf(uf_name='deselect.interatom', spin_id1=':UNK@C12', spin_id2=':UNK@H17')
self._execute_uf(uf_name='deselect.interatom', spin_id1=':UNK@C12', spin_id2=':UNK@H18')

# File list.
align_list = ['Dy', 'Tb', 'Tm', 'Er']

# Load the RDCs and PCSs.
for i in range(len(align_list)):
    # The RDC.
    self._execute_uf(uf_name='rdc.read', align_id=align_list[i], file='rdc.txt', dir=data_path, spin_id1_col=1, spin_id2_col=2, data_col=i+3, error_col=None)
    self._execute_uf(uf_name='rdc.read', align_id=align_list[i], file='rdc_err.txt', dir=data_path, spin_id1_col=1, spin_id2_col=2, data_col=None, error_col=i+3)
    self._execute_uf(uf_name='rdc.display', align_id=align_list[i])

    # The PCS.
    self._execute_uf(uf_name='pcs.read', align_id=align_list[i], file='pcs.txt', dir=data_path, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=1, data_col=i+2, error_col=None)
    self._execute_uf(uf_name='pcs.read', align_id=align_list[i], file='pcs_err.txt', dir=data_path, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=1, data_col=None, error_col=i+2)
    self._execute_uf(uf_name='pcs.display', align_id=align_list[i])

    # The temperature.
    self._execute_uf(uf_name='temperature', id=align_list[i], temp=298)

    # The frequency.
    self._execute_uf(uf_name='frq.set', id=align_list[i], frq=900.015 * 1e6)

# Create a data pipe for the aligned tag structures.
self._execute_uf(uf_name='pipe.create', pipe_name='tag', pipe_type='N-state')

# Load all the tag structures.
NUM_TAG = 10
for i in range(NUM_TAG):
    self._execute_uf(uf_name='structure.read_pdb', file='tag_MCMM4_'+repr(i+1), dir=str_path, set_model_num=i+1, set_mol_name='tag')

# Load the lanthanide atoms.
self._execute_uf(uf_name='structure.load_spins', spin_id='@C1', ave_pos=False)

# Switch back to the main analysis data pipe.
self._execute_uf(uf_name='pipe.switch', pipe_name='lactose')

# Calculate the paramagnetic centre (from the structures in the 'tag' data pipe).
self._execute_uf(uf_name='paramag.centre', atom_id=':4@C1', pipe='tag')

# Set up the model.
self._execute_uf(uf_name='n_state_model.select_model', model=ds.model)

# Set to equal probabilities.
if ds.model == 'population':
    for j in range(NUM_STR):
        self._execute_uf(1.0/NUM_STR, 'p'+repr(j), uf_name='value.set')

# Minimisation.
self._execute_uf('bfgs', constraints=True, max_iter=5, uf_name='minimise')

# Calculate the AIC value.
k, n, chi2 = n_state_model_obj.model_statistics()
ds[ds.current_pipe].aic = chi2 + 2.0*k

# Write out a results file.
self._execute_uf(uf_name='results.write', file='devnull', force=True)

# Show the tensors.
self._execute_uf(uf_name='align_tensor.display')
