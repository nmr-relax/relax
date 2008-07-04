"""Script for consistency testing."""

# Python module imports.
import sys

# Create the run.
name = 'consistency'
pipe.create(name, 'ct')

# Load the sequence.
sequence.read(sys.path[-1] + '/test_suite/system_tests/data/jw_mapping/noe.dat')

# Load the relaxation data.
relax_data.read('R1', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/system_tests/data/jw_mapping/R1.dat')
relax_data.read('R2', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/system_tests/data/jw_mapping/R2.dat')
relax_data.read('NOE', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/system_tests/data/jw_mapping/noe.dat')

# Set the nuclei types
value.set('15N', 'heteronucleus')
value.set('1H', 'proton')

# Set the bond length and CSA values.
value.set(1.02 * 1e-10, 'bond_length')
value.set(-172 * 1e-6, 'csa')

# Set the angle between the 15N-1H vector and the principal axis of the 15N chemical shift tensor
value.set(15.7, 'orientation')

# Set the approximate correlation time.
value.set(13 * 1e-9, 'tc')

# Set the frequency.
consistency_tests.set_frq(frq=600.0 * 1e6)

# Consistency tests.
calc()

# Monte Carlo simulations.
monte_carlo.setup(number=500)
monte_carlo.create_data()
calc()
monte_carlo.error_analysis()

# Create grace files.
grace.write(y_data_type='j0', file='j0.agr', force=True)
grace.write(y_data_type='f_eta', file='f_eta.agr', force=True)
grace.write(y_data_type='f_r2', file='f_r2.agr', force=True)

# View the grace files.
grace.view(file='j0.agr')
grace.view(file='f_eta.agr')
grace.view(file='f_r2.agr')

# Finish.
results.write(file='results', force=True)
state.save('save', force=True)
