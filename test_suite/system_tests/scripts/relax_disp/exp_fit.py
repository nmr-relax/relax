# Script for fitting the 'exp_fit' relaxation dispersion model to synthetic R1rho data.

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Create the data pipe.
pipe.create('exp_fit', 'relax_disp')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting_disp'+sep+'exp_fit_data'

# Create the sequence data.
spin.create(res_name='Asp', res_num=1, spin_name='N')
spin.create(res_name='Gly', res_num=2, spin_name='N')
spin.create(res_name='Lys', res_num=3, spin_name='N')

# Set the relaxation dispersion experiment type.
relax_disp.exp_type('r1rho')

# Set the relaxation dispersion curve type.
relax_disp.select_model('exp_fit')

# The spectral data - spectrum ID, peak lists, offset frequency (Hz), relaxation time period (s), baseplane RMSD estimate.
data = [
    ["nu_1kHz_relaxT_0.01", "nu_1kHz_relaxT_0.01.list", 1000.0, 0.01,   1000],
    ["nu_1kHz_relaxT_0.02", "nu_1kHz_relaxT_0.02.list", 1000.0, 0.02,   1000],
    ["nu_1kHz_relaxT_0.04", "nu_1kHz_relaxT_0.04.list", 1000.0, 0.04,   1000],
    ["nu_1kHz_relaxT_0.06", "nu_1kHz_relaxT_0.06.list", 1000.0, 0.06,   1000],
    ["nu_1kHz_relaxT_0.08", "nu_1kHz_relaxT_0.08.list", 1000.0, 0.08,   1000],
    ["nu_1kHz_relaxT_0.10", "nu_1kHz_relaxT_0.10.list", 1000.0, 0.10,   1000],
    ["nu_1kHz_relaxT_0.12", "nu_1kHz_relaxT_0.12.list", 1000.0, 0.12,   1000],
    ["nu_2kHz_relaxT_0.01", "nu_2kHz_relaxT_0.01.list", 2000.0, 0.01,   1000],
    ["nu_2kHz_relaxT_0.02", "nu_2kHz_relaxT_0.02.list", 2000.0, 0.02,   1000],
    ["nu_2kHz_relaxT_0.04", "nu_2kHz_relaxT_0.04.list", 2000.0, 0.04,   1000],
    ["nu_2kHz_relaxT_0.06", "nu_2kHz_relaxT_0.06.list", 2000.0, 0.06,   1000],
    ["nu_2kHz_relaxT_0.08", "nu_2kHz_relaxT_0.08.list", 2000.0, 0.08,   1000],
    ["nu_2kHz_relaxT_0.10", "nu_2kHz_relaxT_0.10.list", 2000.0, 0.10,   1000],
    ["nu_2kHz_relaxT_0.12", "nu_2kHz_relaxT_0.12.list", 2000.0, 0.12,   1000],
]

# Loop over the spectral data, loading it and setting the metadata.
for i in range(len(data)):
    # Load the peak intensities and set the errors.
    spectrum.read_intensities(file=data[i][1], dir=data_path, spectrum_id=data[i][0], int_method='height', proton='H')
    spectrum.baseplane_rmsd(spectrum_id=data[i][0], error=data[i][4])

    # Set the relaxation dispersion spin-lock field strength (nu1).
    relax_disp.spin_lock_field(spectrum_id=data[i][0], field=data[i][2])

    # Set the relaxation times.
    relax_disp.relax_time(spectrum_id=data[i][0], time=data[i][3])

# Peak intensity error analysis.
spectrum.error_analysis()

# Grid search.
grid_search(inc=5)

# Minimise.
minimise('simplex', constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=3)
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

# Save the program state.
state.save('devnull', force=True)
