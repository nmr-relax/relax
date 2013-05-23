"""Script for testing the fitting of the paramagnetic centre of the PCSs."""

# Python module imports.
from os import sep
import sys

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control import pipes
from status import Status; status = Status()


# Path of the alignment data and structure.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'CaM'
STRUCT_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# Create the data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='para_centre', pipe_type='N-state')

# Set the mode, if not specified by the system test.
if not hasattr(ds, 'mode'):
    ds.mode = 'all'

# The data to use.
rdc_file = 'synth_rdc'
pcs_file = 'synth_pcs'

# Load the CaM structure.
self._execute_uf(uf_name='structure.read_pdb', file='bax_C_1J7P_N_H_Ca', dir=STRUCT_PATH)

# Load the spins.
self._execute_uf(uf_name='structure.load_spins')

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='dipole_pair.define', spin_id1='@N', spin_id2='@H', direct_bond=True)
self._execute_uf(uf_name='dipole_pair.set_dist', spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
self._execute_uf(uf_name='dipole_pair.unit_vectors', ave=False)

# Set the nuclear isotope type.
self._execute_uf(uf_name='spin.isotope', isotope='15N', spin_id='@N')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H')

# Deselect most spins and interatomic data containers (to speed things up).
self._execute_uf(uf_name='deselect.spin')
self._execute_uf(uf_name='select.spin', spin_id=":83")
self._execute_uf(uf_name='select.spin', spin_id=":84")
self._execute_uf(uf_name='select.spin', spin_id=":85")
self._execute_uf(uf_name='select.spin', spin_id=":111")
self._execute_uf(uf_name='select.spin', spin_id=":130")
self._execute_uf(uf_name='select.spin', spin_id=":131")
self._execute_uf(uf_name='select.spin', spin_id=":132")
self._execute_uf(uf_name='select.spin', spin_id=":148")
self._execute_uf(uf_name='deselect.interatom')
self._execute_uf(uf_name='select.interatom', spin_id1=":83")
self._execute_uf(uf_name='select.interatom', spin_id1=":84")
self._execute_uf(uf_name='select.interatom', spin_id1=":85")
self._execute_uf(uf_name='select.interatom', spin_id1=":111")
self._execute_uf(uf_name='select.interatom', spin_id1=":130")
self._execute_uf(uf_name='select.interatom', spin_id1=":131")
self._execute_uf(uf_name='select.interatom', spin_id1=":132")
self._execute_uf(uf_name='select.interatom', spin_id1=":148")

# RDCs.
if ds.mode == 'all':
    self._execute_uf(uf_name='rdc.read', align_id='synth', file=rdc_file, dir=DATA_PATH, spin_id1_col=1, spin_id2_col=2, data_col=3)

# PCSs.
self._execute_uf(uf_name='pcs.read', align_id='synth', file=pcs_file, dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6)

# The temperature.
self._execute_uf(uf_name='spectrometer.temperature', id='synth', temp=303)

# The frequency.
self._execute_uf(uf_name='spectrometer.frequency', id='synth', frq=600.0 * 1e6)

# Set up the model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

# Paramagnetic centre optimisation
real_pos = [32.555, -19.130, 27.775]

#paramag.centre([  32.555,  -19.130,   27.775], fix=False)
self._execute_uf(uf_name='paramag.centre', pos=[ 32, -19, 28], fix=False)

# Set the tensor elements.
cdp.align_tensors[0].set(param='Axx', value=-0.351261/2000)
cdp.align_tensors[0].set(param='Ayy', value=0.556994/2000)
cdp.align_tensors[0].set(param='Axy', value=-0.506392/2000)
cdp.align_tensors[0].set(param='Axz', value=0.560544/2000)
cdp.align_tensors[0].set(param='Ayz', value=-0.286367/2000)

#cdp.align_tensors[0].set(param='Axx', value=0.0)
#cdp.align_tensors[0].set(param='Ayy', value=0.0)
#cdp.align_tensors[0].set(param='Axy', value=0.0)
#cdp.align_tensors[0].set(param='Axz', value=0.0)
#cdp.align_tensors[0].set(param='Ayz', value=0.0)

# Minimisation.
#self._execute_uf(uf_name='grid_search, inc=6)
self._execute_uf(uf_name='minimise', min_algor='simplex', constraints=False, max_iter=500)
#self._execute_uf(uf_name='calc')

# Set up the errors needed for the simulations.
self._execute_uf(uf_name='rdc.set_errors', sd=1.0)
self._execute_uf(uf_name='pcs.set_errors', sd=0.1)

# Monte Carlo simulations.
self._execute_uf(uf_name='monte_carlo.setup', number=3)
self._execute_uf(uf_name='monte_carlo.create_data')
self._execute_uf(uf_name='monte_carlo.initial_values')
self._execute_uf('simplex', constraints=False, max_iter=500, uf_name='minimise')
self._execute_uf(uf_name='monte_carlo.error_analysis')

# Write out a results file.
self._execute_uf(uf_name='results.write', file='devnull', force=True)

## Show the tensors.
#self._execute_uf(uf_name='align_tensor.display')
#
# Print out
print("A:\n%s" % cdp.align_tensors[0].A)
print("centre: %s" % cdp.paramagnetic_centre)
print("centre diff: %s" % (cdp.paramagnetic_centre - real_pos))
print("chi2: %s" % cdp.chi2)

# Map.
#self._execute_uf(uf_name='dx.map', params=['paramag_x', 'paramag_y', 'paramag_z'], inc=10, lower=[30, -20, 26], upper=[33, -18, 30])
