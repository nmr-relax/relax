# Script for CPMG relaxation dispersion curve fitting in the fast-exchange limit.

# Python module imports.
import __main__
from os import sep


# Create the data pipe.
pipe.create('rex', 'relax_disp')

# The path to the data files.
data_path1 = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting_disp'+sep+'Hansen'+sep+'500_MHz'
data_path2 = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting_disp'+sep+'Hansen'+sep+'800_MHz'

# Load the sequence.
sequence.read('fake_sequence.in', dir=__main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting_disp'+sep+'Hansen', res_num_col=1, res_name_col=2)

# Name the spins so they can be matched to the assignments.
spin.name(name='N')

# Set the relaxation dispersion experiment type.
relax_disp.exp_type('cpmg')

# Set the relaxation dispersion curve type.
relax_disp.select_model('fast')

# Relaxation dispersion magnetic field (in Hz).
frq.set(id='500', frq=500.0 * 1e6)
frq.set(id='800', frq=800.0 * 1e6)

# Spectrum names.
names = [
    'reference.in_sparky',
    '66.667.in_sparky',
    '1000.in_sparky',
    '133.33.in_sparky',
    '933.33.in_sparky',
    '200.in_sparky',
    '866.67.in_sparky',
    '266.67.in_sparky',
    '800.in_sparky',
    '333.33.in_sparky',
    '733.33.in_sparky',
    '400.in_sparky',
    '666.67.in_sparky',
    '466.67.in_sparky',
    '600.in_sparky',
    '533.33.in_sparky',
    '133.33.in.bis_sparky',
    '933.33.in.bis_sparky',
    '533.33.in.bis_sparky'
]

# Relaxation dispersion CPMG constant time delay T (in s).
relax_disp.cpmg_delayT(id='500', delayT=0.030)
relax_disp.cpmg_delayT(id='800', delayT=0.030)

# Relaxation dispersion CPMG frequencies (in Hz).
cpmg_frq = [
    None,
    66.667,
    1000,
    133.33,
    933.33,
    200,
    866.67,
    266.67,
    800,
    333.33,
    733.33,
    400,
    666.67,
    466.67,
    600,
    533.33,
    133.33,
    933.33,
    533.33
]

# Loop over the spectra.
for i in xrange(len(names)):
    # Load the peak intensities.
    spectrum.read_intensities(file=names[i], dir=data_path_1, spectrum_id=names[i], int_method='height')
    spectrum.read_intensities(file=names[i], dir=data_path_2, spectrum_id=names[i], int_method='height')

    # Set the relaxation dispersion CPMG frequencies.
    relax_disp.cpmg_frq(cpmg_frq=cpmg_frq[i], spectrum_id=names[i])

# Specify the duplicated spectra.
spectrum.replicated(spectrum_ids=['133.33.in_sparky', '133.33.in.bis_sparky'])
spectrum.replicated(spectrum_ids=['533.33.in_sparky', '533.33.in.bis_sparky'])
spectrum.replicated(spectrum_ids=['933.33.in_sparky', '933.33.in.bis_sparky'])

# Peak intensity error analysis.
spectrum.error_analysis()

# Deselect unresolved spins.
deselect.read(file='unresolved', dir=data_path_1)
deselect.read(file='unresolved', dir=data_path_2)

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
