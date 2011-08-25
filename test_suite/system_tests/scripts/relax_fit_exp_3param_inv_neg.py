# Script for relaxation curve fitting.

# Python module imports.
from os import sep
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Missing intensity type (allow this script to run outside of the system test framework).
if not hasattr(ds, 'int_type'):
    ds.int_type = 'height'


# Create the data pipe.
pipe.create('rx', 'relax_fit')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting'

# Load the sequence.
sequence.read('Ap4Aase.seq', dir=status.install_path + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)

# Deselect unresolved spins.
deselect.read(file='unresolved', dir=data_path, res_num_col=1)

# Name the spins so they can be matched to the assignments.
spin.name(name='N')

# Spectrum names.
names = [
    'T1_inv-recov_200_ms',
    'T1_inv-recov_450_ms',
    'T1_inv-recov_750_ms',
    'T1_inv-recov_750_ms_bis',
    'T1_inv-recov_1100_ms',
    'T1_inv-recov_1500_ms',
    'T1_inv-recov_1950_ms',
    'T1_inv-recov_1950_ms_bis',
    'T1_inv-recov_2450_ms'
]

# Relaxation times (in seconds).
times = [
    0.2,
    0.45,
    0.75,
    1.1,
    1.5,
    1.95,
    2.45
]

# Loop over the spectra.
for i in xrange(len(names)):
    # Load the peak intensities.
    spectrum.read_intensities(file=names[i]+'.list', dir=data_path, spectrum_id=names[i], int_method=ds.int_type)

    # Set the relaxation times.
    relax_fit.relax_time(time=times[i], spectrum_id=names[i])

# Specify the duplicated spectra.
spectrum.replicated(spectrum_ids=['T1_inv-recov_750_ms', 'T1_inv-recov_750_ms_bis'])
spectrum.replicated(spectrum_ids=['T1_inv-recov_1950_ms', 'T1_inv-recov_1950_ms_bis'])

# Peak intensity error analysis.
spectrum.error_analysis()

# Set the relaxation curve type.
relax_fit.select_model('exp_3param_inv_neg')

# Grid search.
grid_search(inc=11)

# Minimise.
minimise('simplex', constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=3)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', constraints=False)
monte_carlo.error_analysis()

# Save the relaxation rates.
value.write(param='rx', file='devnull', force=True)

# Save the results.
results.write(file='devnull', force=True)

# Create Grace plots of the data.
grace.write(y_data_type='chi2', file='devnull', force=True)    # Minimised chi-squared value.
grace.write(y_data_type='i0', file='devnull', force=True)    # Initial peak intensity.
grace.write(y_data_type='rx', file='devnull', force=True)    # Relaxation rate.
grace.write(x_data_type='relax_times', y_data_type='int', file='devnull', force=True)    # Average peak intensities.
grace.write(x_data_type='relax_times', y_data_type='int', norm=True, file='devnull', force=True)    # Average peak intensities (normalised).

# Save the program state.
state.save('devnull', force=True)
