# Script for calculating NOEs.

# Create the run
name = 'noe'
pipe.create('noe')

# Load the backbone amide 15N spins from a PDB file.
structure.read_pdb('Ap4Aase_new_3.pdb')
structure.load_spins(spin_id='@N')

# Load the reference spectrum and saturated spectrum peak intensities.
noe.read(file='ref.list', spectrum_type='ref')
noe.read(file='sat.list', spectrum_type='sat')

# Set the errors.
noe.error(error=3600, spectrum_type='ref')
noe.error(error=3000, spectrum_type='sat')

# Individual residue errors.
noe.error(error=122000, spectrum_type='ref', res_num=114)
noe.error(error=8500, spectrum_type='sat', res_num=114)

# Unselect unresolved residues.
unselect.read(file='unresolved')

# Calculate the NOEs.
calc(name)

# Save the NOEs.
value.write(param='noe', file='noe.out', force=1)

# Create grace files.
grace.write(y_data_type='ref', file='ref.agr', force=1)
grace.write(y_data_type='sat', file='sat.agr', force=1)
grace.write(y_data_type='noe', file='noe.agr', force=1)

# View the grace files.
grace.view(file='ref.agr')
grace.view(file='sat.agr')
grace.view(file='noe.agr')

# Write the results.
results.write(file='results', dir=None, force=1)

# Save the program state.
state.save('save', force=1)
