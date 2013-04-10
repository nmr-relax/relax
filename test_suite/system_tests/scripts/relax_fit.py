# Script for relaxation curve fitting.

# Python module imports.
from os import sep
import sys

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Missing intensity type (allow this script to run outside of the system test framework).
if not hasattr(ds, 'int_type'):
    ds.int_type = 'height'

# Missing temporary directory.
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = 'temp'

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
    'T2_ncyc1_ave',
    'T2_ncyc1b_ave',
    'T2_ncyc2_ave',
    'T2_ncyc4_ave',
    'T2_ncyc4b_ave',
    'T2_ncyc6_ave',
    'T2_ncyc9_ave',
    'T2_ncyc9b_ave',
    'T2_ncyc11_ave',
    'T2_ncyc11b_ave'
]

# Relaxation times (in seconds).
times = [
    0.0176,
    0.0176,
    0.0352,
    0.0704,
    0.0704,
    0.1056,
    0.1584,
    0.1584,
    0.1936,
    0.1936
]

# Load the data twice to test data deletion.
for iter in range(2):
    # Loop over the spectra.
    for i in range(len(names)):
        # Load the peak intensities.
        spectrum.read_intensities(file=names[i]+'.list', dir=data_path, spectrum_id=names[i], int_method=ds.int_type)

        # Set the relaxation times.
        relax_fit.relax_time(time=times[i], spectrum_id=names[i])

    # Specify the duplicated spectra.
    spectrum.replicated(spectrum_ids=['T2_ncyc1_ave', 'T2_ncyc1b_ave'])
    spectrum.replicated(spectrum_ids=['T2_ncyc4_ave', 'T2_ncyc4b_ave'])
    spectrum.replicated(spectrum_ids=['T2_ncyc9b_ave', 'T2_ncyc9_ave'])
    spectrum.replicated(spectrum_ids=['T2_ncyc11_ave', 'T2_ncyc11b_ave'])

    # Peak intensity error analysis.
    spectrum.error_analysis()

    # Delete the data.
    if iter == 0:
        for i in range(len(names)):
            spectrum.delete(names[i])

# Set the relaxation curve type.
relax_fit.select_model('exp')

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
grace.write(y_data_type='chi2', file='chi2.agr', dir=ds.tmpdir, force=True)    # Minimised chi-squared value.
grace.write(y_data_type='i0', file='i0.agr', dir=ds.tmpdir, force=True)    # Initial peak intensity.
grace.write(y_data_type='rx', file='rx.agr', dir=ds.tmpdir, force=True)    # Relaxation rate.
grace.write(y_data_type='rx', file='rx_err.agr', dir=ds.tmpdir, plot_data='error', force=True)    # Relaxation rate.
grace.write(y_data_type='rx', file='rx_sim.agr', dir=ds.tmpdir, plot_data='sim', force=True)    # Relaxation rate.
grace.write(x_data_type='i0', y_data_type='rx', file='i0_vs_rx.agr', dir=ds.tmpdir, force=True)    # Relaxation rate.
grace.write(x_data_type='i0', y_data_type='rx', file='i0_vs_rx_err.agr', plot_data='error', dir=ds.tmpdir, force=True)    # Relaxation rate.
grace.write(x_data_type='i0', y_data_type='rx', file='i0_vs_rx_sim.agr', plot_data='sim', dir=ds.tmpdir, force=True)    # Relaxation rate.
grace.write(x_data_type='relax_times', y_data_type='intensities', file='curves.agr', dir=ds.tmpdir, force=True)    # Average peak intensities.
grace.write(x_data_type='relax_times', y_data_type='intensities', norm=True, file='curves_norm.agr', dir=ds.tmpdir, force=True)    # Average peak intensities (normalised).

# Create Grace plots with the axes reversed.
grace.write(x_data_type='chi2', y_data_type='res_num', file='chi2_rev.agr', dir=ds.tmpdir, force=True)    # Minimised chi-squared value.
grace.write(x_data_type='i0', y_data_type='res_num', file='i0_rev.agr', dir=ds.tmpdir, force=True)    # Initial peak intensity.
grace.write(x_data_type='rx', y_data_type='res_num', file='rx_rev.agr', dir=ds.tmpdir, force=True)    # Relaxation rate.
grace.write(x_data_type='rx', y_data_type='res_num', file='rx_err_rev.agr', dir=ds.tmpdir, plot_data='error', force=True)    # Relaxation rate.
grace.write(x_data_type='rx', y_data_type='res_num', file='rx_sim_rev.agr', dir=ds.tmpdir, plot_data='sim', force=True)    # Relaxation rate.
grace.write(x_data_type='intensities', y_data_type='relax_times', file='curves_rev.agr', dir=ds.tmpdir, force=True)    # Average peak intensities.
grace.write(x_data_type='intensities', y_data_type='relax_times', norm=True, file='curves_norm_rev.agr', dir=ds.tmpdir, force=True)    # Average peak intensities (normalised).

# Save the program state.
state.save('devnull', force=True)
