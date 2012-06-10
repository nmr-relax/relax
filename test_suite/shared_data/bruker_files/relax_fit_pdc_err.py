# Script for relaxation curve fitting.

# relax module imports.
from generic_fns.mol_res_spin import return_spin
from relax_io import extract_data


# Create the data pipe.
pipe.create('rx', 'relax_fit')

# Load the sequence.
sequence.read('seq', res_num_col=2, res_name_col=1)

# Name the spins so they can be matched to the assignments.
spin.name(name='N')

# Spectrum names.
names = [        
    '0.01',
    '0.05',
    '0.10',
    '0.10b',
    '0.20',
    '0.30',
    '0.40',
    '0.50',
    '0.50b',
    '0.70',
    '1.00',
    '1.50'
]

# Relaxation times (in seconds).
times = [
    0.01000000,
    0.05000000,
    0.10000000,
    0.10000000,
    0.20000000,
    0.30000000,
    0.40000000,
    0.50000000,
    0.50000000,
    0.70000000,
    1.00000000,
    1.50000000
]

# The error file.
err_lines = extract_data('errors_R1.txt')

# Loop over the spectra.
for i in xrange(len(times)):
    # Load the peak intensities.
    spectrum.read_intensities(file='heights_R1.txt', spectrum_id=names[i], int_method='height', res_num_col=2, res_name_col=1, int_col=i+3)

    # Set the relaxation times.
    relax_fit.relax_time(time=times[i], spectrum_id=names[i])

    # The errors.
    for j in range(len(err_lines)):
        # Skip comments.
        if err_lines[j][0][0] == '#':
            continue

        # The spin ID.
        spin_id = ':%s' % err_lines[j][1]
        spin = return_spin(spin_id)

        # Set the error.
        if not hasattr(spin, 'intensity_err'):
            spin.intensity_err = {}
        spin.intensity_err[names[i]] = float(err_lines[j][i+2])

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Grid search.
grid_search(inc=11)

# Minimise.
minimise('simplex', constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=500)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', constraints=False)
monte_carlo.error_analysis()

# Save the relaxation rates.
value.write(param='rx', file='r1_pdc_err', force=True)

# Save the program state.
state.save('state', force=True)
