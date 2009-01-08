# Script for CPMG relaxation dispersion curve fitting in the fast-exchange limit.

import sys


# Create the data pipe.
pipe.create('rex', 'relax_disp')

# The path to the data files.
data_path = sys.path[-1] + '/test_suite/shared_data/disp_curve_fitting'

# Load the sequence.
sequence.read('Ap4Aase.seq', dir=sys.path[-1] + '/test_suite/shared_data')

# Name the spins so they can be matched to the assignments.
spin.name(name='N')

# Spectrum names.
names = [
    'T2_ncyc1_ave'
]

# Relaxation dispersion magnetic field (in Hz).
frq.set(id='600', frq=600.0 * 1e6)

# Relaxation dispersion CPMG frequencies (in Hz).
cpmg_frq = [
    0.1936
]

# Set the relaxation dispersion experiment type.
relax_disp.exp_type('cpmg')

# Set the relaxation dispersion curve type.
relax_disp.select_model('fast')

# Loop over the spectra.
for i in xrange(len(names)):
    # Load the peak intensities.
    spectrum.read_intensities(file=names[i]+'.list', dir=data_path, spectrum_id=names[i], int_method='height')

    # Set the relaxation dispersion CPMG frequencies.
    relax_disp.relax_time(frq=frq[i], spectrum_id=names[i])

# Specify the duplicated spectra.
#spectrum.replicated(spectrum_ids=['T2_ncyc1_ave', 'T2_ncyc1b_ave'])

# Peak intensity error analysis.
spectrum.error_analysis()

# Deselect unresolved spins.
deselect.read(file='unresolved', dir=data_path)

# Grid search.
grid_search(inc=11)

# Minimise.
minimise('simplex', constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=10)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', constraints=False)
monte_carlo.error_analysis()

# Save the relaxation dispersion parameters.
value.write(param='rex', file='devnull', force=True)

# Save the results.
results.write(file='devnull', force=True)

# Create Grace plots of the data.
grace.write(y_data_type='chi2', file='devnull', force=True)    # Minimised chi-squared value.
grace.write(y_data_type='R2', file='devnull', force=True)    # R2 parameter without Rex contribution.
grace.write(y_data_type='Rex', file='devnull', force=True)    # Chemical exchange contribution to observed R2.
grace.write(y_data_type='kex', file='devnull', force=True)    # Exchange rate.
grace.write(x_data_type='frq', y_data_type='int', file='devnull', force=True)    # Average peak intensities.
grace.write(x_data_type='frq', y_data_type='int', norm=True, file='devnull', force=True)    # Average peak intensities (normalised).

# Save the program state.
state.save('devnull', force=True)
