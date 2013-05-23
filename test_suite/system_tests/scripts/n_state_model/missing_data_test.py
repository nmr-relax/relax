# Script for determining populations for lactose conformations using RDCs and PCSs.

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'dna'
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'missing_data'

# Create the data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='missing_data_test', pipe_type='N-state')

# Load the structure.
self._execute_uf(uf_name='structure.read_pdb', file='LE_trunc.pdb', dir=str_path, set_mol_name='LE')

# Load the sequence information.
self._execute_uf(uf_name='structure.load_spins', spin_id='@C*', ave_pos=False)
self._execute_uf(uf_name='structure.load_spins', spin_id='@H*', ave_pos=False)

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='dipole_pair.define', spin_id1='@C*', spin_id2='@H*', direct_bond=True)
self._execute_uf(uf_name='dipole_pair.set_dist', spin_id1='@C*', spin_id2='@H*', ave_dist=1.10 * 1e-10)
self._execute_uf(uf_name='dipole_pair.unit_vectors', ave=False)

# Set the nuclear isotope type.
self._execute_uf(uf_name='spin.isotope', isotope='13C', spin_id='@C*')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H*')

# File list.
align_list = ['Dy', 'Tb', 'Tm', 'Er']

# Load the RDCs and PCSs.
for i in range(len(align_list)):
    # The RDC.
    if i != 1:
        self._execute_uf(uf_name='rdc.read', align_id=align_list[i], file='missing_rdc_%i' % i, dir=data_path, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=None)
        self._execute_uf(uf_name='rdc.display', align_id=align_list[i])

    # The PCS.
    if i != 2:
        self._execute_uf(uf_name='pcs.read', align_id=align_list[i], file='missing_pcs_%i' % i, dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=None, spin_name_col=5, data_col=6, error_col=None)
        self._execute_uf(uf_name='pcs.display', align_id=align_list[i])

    # The temperature.
    self._execute_uf(uf_name='spectrometer.temperature', id=align_list[i], temp=298)

    # The frequency.
    self._execute_uf(uf_name='spectrometer.frequency', id=align_list[i], frq=799.75376122 * 1e6)

# Set some errors.
self._execute_uf(uf_name='rdc.set_errors', sd=1.0)
self._execute_uf(uf_name='pcs.set_errors', sd=0.1)

# Set the paramagnetic centre.
self._execute_uf(uf_name='paramag.centre', pos=[1, 2, -30])

# Set up the model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

# Minimisation.
self._execute_uf(uf_name='minimise', min_algor='bfgs', constraints=True)

# Monte Carlo simulations.
self._execute_uf(uf_name='monte_carlo.setup', number=3)
self._execute_uf(uf_name='monte_carlo.create_data')
self._execute_uf(uf_name='monte_carlo.initial_values')
self._execute_uf(uf_name='minimise', min_algor='bfgs', constraints=True)
self._execute_uf(uf_name='monte_carlo.error_analysis')

# Write out a results file.
self._execute_uf(uf_name='results.write', file='devnull', force=True)

# Show the tensors.
self._execute_uf(uf_name='align_tensor.display')
