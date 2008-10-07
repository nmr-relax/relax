# Script for calculating NOEs.
import sys

# Create the NOE data pipe.
pipe.create('NOE', 'noe')

# Load the sequence.
sequence.read(file='Ap4Aase.seq', dir=sys.path[-1] + '/test_suite/shared_data')

# Load the reference spectrum and saturated spectrum peak intensities.
noe.read(file='ref_ave.list', dir=sys.path[-1] + '/test_suite/shared_data/peak_lists', spectrum_type='ref')
noe.read(file='sat_ave.list', dir=sys.path[-1] + '/test_suite/shared_data/peak_lists', spectrum_type='sat')

# Set the errors.
noe.error(error=3600, spectrum_type='ref')
noe.error(error=3000, spectrum_type='sat')

# Individual residue errors.
noe.error(error=122000, spectrum_type='ref', res_num=5)
noe.error(error=8500, spectrum_type='sat', res_num=5)

# Deselect unresolved residues.
deselect.read(file='unresolved', dir=sys.path[-1] + '/test_suite/shared_data/curve_fitting')

# Calculate the NOEs.
calc()

# Save the NOEs.
value.write(param='noe', file='devnull', force=True)

# Create grace files.
grace.write(y_data_type='ref', file='devnull', force=True)
grace.write(y_data_type='sat', file='devnull', force=True)
grace.write(y_data_type='noe', file='devnull', force=True)

# Write the results.
results.write(file='devnull', dir=None, force=True)

# Save the program state.
state.save('devnull', force=True)
