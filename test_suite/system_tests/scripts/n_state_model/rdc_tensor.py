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
pipe.create(tag, 'N-state')

# Load the CaM structures.
structure.read_pdb('bax_C_1J7P_N_H_Ca.pdb', dir=STRUCT_PATH)

# Load the spins.
structure.load_spins('@N', ave_pos=False)
structure.load_spins('@H', ave_pos=False)

# Load the NH vectors.
structure.vectors('H', '@N', ave=False)

# Set the values needed to calculate the dipolar constant.
value.set(NH_BOND_LENGTH_RDC, 'r')
value.set('15N', 'heteronuc_type')
value.set('1H', 'proton_type')

# RDCs.
rdc.read(tag, file='rdc_dy', dir=DATA_PATH, res_num_col=1, spin_name_col=2, data_col=3, error_col=4, neg_g_corr=True)

# Set up the model.
n_state_model.select_model('fixed')

# Minimisation.
grid_search(inc=3)
minimise('newton', constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=3)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('newton', constraints=False)
monte_carlo.error_analysis()

# Show the tensors.
align_tensor.display(tag)

# Back calc.
rdc.back_calc()

# Q-factors.
rdc.calc_q_factors()

# Correlation plots.
rdc.corr_plot(file="devnull", force=True)
