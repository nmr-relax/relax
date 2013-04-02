"""This system test script catches the relaxation curve-fitting optimisation bug submitted by Romel Bobby.

The bug is:
    - Bug #19887 (https://gna.org/bugs/?19887).
"""

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# The data path.
DATA_PATH = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'peak_lists' + sep + 'bug_19887' + sep

# Create the 'rx' data pipe.
pipe.create('rx', 'relax_fit')

# Load the backbone amide 15N spins from a PDB file.
spin.create(mol_name='IL6_mf_mol1', res_name='GLU', res_num=24, spin_name='N')
spin.create(mol_name='IL6_mf_mol1', res_name='LYS', res_num=28, spin_name='N')
spin.create(mol_name='IL6_mf_mol1', res_name='GLN', res_num=29, spin_name='N')

# Spectrum names.
names = [
    'T1_1204.04',
    'T1_1804.04',
    'T1_2754.04',
    'T1_304.04',
    'T1_304.040'
]

# Relaxation times (in seconds).
times = [
    1.204,
    1.804,
    2.754,
    0.304,
    0.304
]

# Loop over the spectra.
for i in range(len(names)):
    # Load the peak intensities.
    spectrum.read_intensities(file=names[i]+'.list', dir=DATA_PATH, spectrum_id=names[i], int_method='height')

    # Set the relaxation times.
    relax_fit.relax_time(time=times[i], spectrum_id=names[i])

# Specify the duplicated spectra.
spectrum.replicated(spectrum_ids=['T1_304.04', 'T1_304.040'])

# Peak intensity error analysis.
spectrum.error_analysis()

# Deselect unresolved spins.
# deselect.read(file='unresolved', mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5)

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Grid search.
grid_search(inc=11)

# Minimise.
minimise('simplex', scaling=False, constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=5)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', scaling=False, constraints=False)
monte_carlo.error_analysis()
