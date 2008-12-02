# Script for calculating NOEs.
import sys


# Create the NOE data pipe.
pipe.create('NOE', 'noe')

# Load the sequence.
sequence.read(file='Ap4Aase.seq', dir=sys.path[-1] + '/test_suite/shared_data')

# Name the spins so they can be matched to the assignments.
spin.name(name='N')

# Load the reference spectrum and saturated spectrum peak intensities.
spectrum.read_intensities(file='ref_ave.list', dir=sys.path[-1] + '/test_suite/shared_data/peak_lists', spectrum_id='ref_ave')
spectrum.read_intensities(file='sat_ave.list', dir=sys.path[-1] + '/test_suite/shared_data/peak_lists', spectrum_id='sat_ave')

# Set the spectrum types.
noe.spectrum_type('ref', 'ref_ave')
noe.spectrum_type('sat', 'sat_ave')

# Set the errors.
spectrum.baseplane_rmsd(error=3600, spectrum_id='ref_ave')
spectrum.baseplane_rmsd(error=3000, spectrum_id='sat_ave')

# Individual residue errors.
spectrum.baseplane_rmsd(error=122000, spectrum_id='ref_ave', spin_id=":5")
spectrum.baseplane_rmsd(error=8500, spectrum_id='sat_ave', spin_id=":5")

# Peak intensity error analysis.
spectrum.error_analysis()

# Deselect unresolved residues.
deselect.read(file='unresolved', dir=sys.path[-1] + '/test_suite/shared_data/curve_fitting')

# Calculate the NOEs.
calc()

# Save the NOEs.
value.write(param='noe', file='devnull', force=True)

# Create grace files.
grace.write(y_data_type='ref_ave', file='devnull', force=True)
grace.write(y_data_type='sat_ave', file='devnull', force=True)
grace.write(y_data_type='noe', file='devnull', force=True)

# Write the results.
results.write(file='devnull', dir=None, force=True)

# Save the program state.
state.save('devnull', force=True)
