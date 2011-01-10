"""Script for consistency testing."""

# Python module imports.
from os import devnull, sep
import sys

# relax module imports.
from status import Status; status = Status()

# Create the run.
name = 'consistency'
pipe.create(name, 'ct')

# Load the sequence.
sequence.read(status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'noe.dat', res_num_col=1, res_name_col=2)

# Load the relaxation data.
relax_data.read('R1', '600', 600.0 * 1e6, status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'R1.dat', res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read('R2', '600', 600.0 * 1e6, status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'R2.dat', res_num_col=1, res_name_col=2, data_col=3, error_col=4)
relax_data.read('NOE', '600', 600.0 * 1e6, status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'noe.dat', res_num_col=1, res_name_col=2, data_col=3, error_col=4)

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
grace.write(y_data_type='j0', file='devnull', force=True)
grace.write(y_data_type='f_eta', file='devnull', force=True)
grace.write(y_data_type='f_r2', file='devnull', force=True)

# Finish.
results.write(file='devnull', force=True)
state.save('devnull', force=True)
