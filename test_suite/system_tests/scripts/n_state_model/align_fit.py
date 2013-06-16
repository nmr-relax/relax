"""Script for testing the fitting an alignment tensor to RDCs or PCSs."""

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Path of the alignment data and structure.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'CaM'
STRUCT_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# Create the data pipe.
self._execute_uf('rdc', 'N-state', uf_name='pipe.create')

# Set the mode, if not specified by the system test.
if not hasattr(ds, 'mode'):
    ds.mode = 'all'

# The data to use.
if hasattr(ds, 'rand') and ds.rand:
    rdc_file = 'synth_rdc_rand'
    pcs_file = 'synth_pcs_rand'
else:
    rdc_file = 'synth_rdc'
    pcs_file = 'synth_pcs'

# Load the CaM structure.
self._execute_uf(uf_name='structure.read_pdb', file='bax_C_1J7P_N_H_Ca', dir=STRUCT_PATH)

# Load the spins.
self._execute_uf(uf_name='structure.load_spins')

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='interatom.define', spin_id1='@N', spin_id2='@H', direct_bond=True)
self._execute_uf(uf_name='interatom.set_dist', spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
self._execute_uf(uf_name='interatom.unit_vectors', ave=False)

# Set the nuclear isotope.
self._execute_uf(uf_name='spin.isotope', isotope='15N', spin_id='@N')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H')

# RDCs.
if ds.mode in ['rdc', 'all']:
    self._execute_uf(uf_name='rdc.read', align_id='synth', file=rdc_file, dir=DATA_PATH, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=None)

# PCSs.
if ds.mode in ['pcs', 'all']:
    self._execute_uf(uf_name='pcs.read', align_id='synth', file=pcs_file, dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6)

    # Set the paramagnetic centre.
    self._execute_uf(uf_name='paramag.centre', atom_id=':1000@CA')

    # The temperature.
    self._execute_uf(uf_name='spectrometer.temperature', id='synth', temp=303)

    # The frequency.
    self._execute_uf(uf_name='spectrometer.frequency', id='synth', frq=600.0 * 1e6)

# Set up the model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

# Set the tensor elements.
#cdp.align_tensors[0].Axx = -0.351261/2000
#cdp.align_tensors[0].Ayy = 0.556994/2000
#cdp.align_tensors[0].Axy = -0.506392/2000
#cdp.align_tensors[0].Axz = 0.560544/2000
#cdp.align_tensors[0].Ayz = -0.286367/2000

# Minimisation.
self._execute_uf(uf_name='grid_search', inc=3)
self._execute_uf('simplex', constraints=False, max_iter=500, uf_name='minimise')

# Set up the errors needed for the simulations.
if ds.mode in ['rdc', 'all']:
    self._execute_uf(uf_name='rdc.set_errors', sd=1.0)
if ds.mode in ['pcs', 'all']:
    self._execute_uf(uf_name='pcs.set_errors', sd=0.1)

# Monte Carlo simulations.
self._execute_uf(uf_name='monte_carlo.setup', number=3)
self._execute_uf(uf_name='monte_carlo.create_data')
self._execute_uf(uf_name='monte_carlo.initial_values')
self._execute_uf('bfgs', constraints=False, max_iter=5, uf_name='minimise')
self._execute_uf(uf_name='monte_carlo.error_analysis')

# Write out a results file.
self._execute_uf('devnull', force=True, uf_name='results.write')

# Show the tensors.
self._execute_uf(uf_name='align_tensor.display')

# Print the contents of the current data pipe (for debugging Q-values).
print(cdp)
print(cdp.align_tensors[0])
