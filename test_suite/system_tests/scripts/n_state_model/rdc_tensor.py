# Python module imports.
from os import sep

# relax module imports.
from physical_constants import NH_BOND_LENGTH_RDC
from status import Status; status = Status()


# Path of the alignment data and structure.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'CaM'
STRUCT_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# The tag.
tag = "Dy C-dom"

# Create the data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name=tag, pipe_type='N-state')

# Load the CaM structures.
self._execute_uf(uf_name='structure.read_pdb', file='bax_C_1J7P_N_H_Ca.pdb', dir=STRUCT_PATH)

# Load the spins.
self._execute_uf(uf_name='structure.load_spins', spin_id='@N', ave_pos=False)
self._execute_uf(uf_name='structure.load_spins', spin_id='@H', ave_pos=False)

# Load the NH vectors.
self._execute_uf('H', '@N', ave=False, uf_name='structure.vectors')

# Set the values needed to calculate the dipolar constant.
self._execute_uf(NH_BOND_LENGTH_RDC, 'r', uf_name='value.set')
self._execute_uf('15N', 'heteronuc_type', uf_name='value.set')
self._execute_uf('1H', 'proton_type', uf_name='value.set')

# RDCs.
self._execute_uf(uf_name='rdc.read', align_id=tag, file='rdc_dy', dir=DATA_PATH, res_num_col=1, spin_name_col=2, data_col=3, error_col=4, neg_g_corr=True)

# Set up the model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

# Minimisation.
self._execute_uf(uf_name='grid_search', inc=3)
self._execute_uf(uf_name='minimise', min_algor='newton', constraints=False)

# Monte Carlo simulations.
self._execute_uf(uf_name='monte_carlo.setup', number=3)
self._execute_uf(uf_name='monte_carlo.create_data')
self._execute_uf(uf_name='monte_carlo.initial_values')
self._execute_uf(uf_name='minimise', min_algor='newton', constraints=False)
self._execute_uf(uf_name='monte_carlo.error_analysis')

# Show the tensors.
self._execute_uf(uf_name='align_tensor.display', align_id=tag)

# Back calc.
self._execute_uf(uf_name='rdc.back_calc')

# Q-factors.
self._execute_uf(uf_name='rdc.calc_q_factors')

# Correlation plots.
self._execute_uf(uf_name='rdc.corr_plot', file="devnull", force=True)
