# Script for testing the zooming grid search in the relaxation curve fitting.

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


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
        spectrum.read_intensities(file=names[i]+'.list', dir=data_path, spectrum_id=names[i], int_method='height')

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

# Only select a single spin for speed.
select.spin(':4', change_all=True)

# Zooming grid search, starting with a zoom level of 0 for the original grid.
for zoom in range(50):
    # Set the zoom level.
    minimise.grid_zoom(level=zoom/0.5)

    # The grid search.
    minimise.grid_search(inc=11)
