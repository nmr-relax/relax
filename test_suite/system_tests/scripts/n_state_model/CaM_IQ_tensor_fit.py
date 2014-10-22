# Tensor optimisation.

# Python imports.
from numpy import array
from os import sep

# relax imports.
from lib.physical_constants import NH_BOND_LENGTH_RDC
from status import Status; status = Status()


# Path of the alignment data and structure.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'CaM_IQ'
STRUCT_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# Create a data pipe for all the data.
pipe.create('CaM N-dom', 'N-state')

# Load the CaM structure.
structure.read_pdb('2BE6_core_I_IV.pdb', dir=STRUCT_PATH, set_mol_name=['CaM_A', 'IQ_A', 'Metals_A', 'CaM_B', 'IQ_B', 'Metals_B', 'CaM_C', 'IQ_C', 'Metals_C'])

# Load the spins.
structure.load_spins('@N', from_mols=['CaM_A', 'CaM_B', 'CaM_C'], mol_name_target='CaM', ave_pos=False)
structure.load_spins('@H', from_mols=['CaM_A', 'CaM_B', 'CaM_C'], mol_name_target='CaM', ave_pos=False)

# Select only the superimposed spins (skipping mobile residues :2-4,42,56-57,76-80, identified from model-free order parameters).
select.spin(':5-31,53-55,58-75', change_all=True)
select.display()

# Define the magnetic dipole-dipole relaxation interaction.
interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=NH_BOND_LENGTH_RDC)
interatom.unit_vectors(ave=False)

# Set the nuclear isotope and element.
spin.isotope(isotope='15N', spin_id='@N')
spin.isotope(isotope='1H', spin_id='@H')

# The alignment data.
align_data = [
    ['dy', 'RDC_DY_111011_spinID.txt', 'PCS_DY_200911.txt', 900.00423401],
    ['tb', 'RDC_TB_111011_spinID.txt', 'PCS_TB_200911.txt', 900.00423381],
    ['tm', 'RDC_TM_111011_spinID.txt', 'PCS_TM_200911.txt', 900.00423431],
    ['er', 'RDC_ER_111011_spinID.txt', 'PCS_ER_200911.txt', 899.90423151],
    ['yb', 'RDC_YB_110112_spinID.txt', 'PCS_YB_211111.txt', 899.90423111],
    ['ho', 'RDC_HO_300512_spinID.txt', 'PCS_HO_300412.txt', 899.80423481]
]

# Loop over the alignments.
for i in range(len(align_data)):
    # Alias the data.
    TAG = align_data[i][0]
    RDC_FILE = align_data[i][1]
    PCS_FILE = align_data[i][2]
    FRQ = align_data[i][3]

    # RDCs.
    rdc.read(align_id=TAG, file=RDC_FILE, dir=DATA_PATH, data_type='D', spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)

    # PCSs.
    pcs.read(align_id=TAG, file=PCS_FILE, dir=DATA_PATH, res_num_col=1, data_col=2, error_col=4, spin_id='@N')
    pcs.read(align_id=TAG, file=PCS_FILE, dir=DATA_PATH, res_num_col=1, data_col=3, error_col=4, spin_id='@H')

    # The temperature.
    spectrometer.temperature(id=TAG, temp=303.0)

    # The frequency.
    spectrometer.frequency(id=TAG, frq=FRQ, units='MHz')

# The paramagnetic centre (average Ca2+ position).
ave = array([6.382, 9.047, 14.457]) + array([6.031, 8.301, 13.918]) + array([6.345, 8.458, 13.868])
ave = ave / 3
paramag.centre(pos=ave)

# Set up the model.
n_state_model.select_model('fixed')

# Tensor optimisation.
print("\n\n# Tensor optimisation.\n\n")
minimise.grid_search(inc=3)
minimise.execute('newton', constraints=False)
state.save('devnull', force=True)

# PCS structural noise.
print("\n\n# Tensor optimisation with PCS structural noise.\n\n")
pcs.structural_noise(rmsd=0.3, sim_num=100, file='devnull', force=True)

# Optimisation of everything.
paramag.centre(fix=False)
minimise.execute('bfgs', constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=3)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise.execute('bfgs', constraints=False, max_iter=5)
monte_carlo.error_analysis()

# Show the tensors.
align_tensor.display()

# Q-factors.
rdc.calc_q_factors()
pcs.calc_q_factors()

# Correlation plots.
rdc.corr_plot(file="devnull", force=True)
pcs.corr_plot(file="devnull", force=True)

# Save the program state.
state.save('devnull', force=True)
