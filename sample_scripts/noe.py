# Script for calculating NOEs.

# Create the run
run = 'noe'
run.create(run, 'noe')

# Load the sequence from a PDB file.
pdb(run, 'Ap4Aase_new_3.pdb', load_seq=1)

# Load the reference spectrum and saturated spectrum peak intensities.
noe.read(run, file='ref.list', spectrum_type='ref')
noe.read(run, file='sat.list', spectrum_type='sat')
#noe.read(run, file='ref.text', spectrum_type='ref', format='xeasy')
#noe.read(run, file='sat.text', spectrum_type='sat', format='xeasy')

# Set the errors.
noe.error(run, error=3600, spectrum_type='ref')
noe.error(run, error=3000, spectrum_type='sat')

# Individual residue errors.
noe.error(run, error=122000, spectrum_type='ref', res_num=114)
noe.error(run, error=8500, spectrum_type='sat', res_num=114)

# Unselect unresolved residues.
unselect.read(run, file='unresolved')

# Calculate the NOEs.
calc(run)

# Save the NOEs.
value.write(run, data_type='noe', file='noe.out', force=1)

# Create grace files.
grace.write(run, data_type='ref', file='ref.agr', force=1)
grace.write(run, data_type='sat', file='sat.agr', force=1)
grace.write(run, data_type='noe', file='noe.agr', force=1)

# View the grace files.
grace.view(file='ref.agr')
grace.view(file='sat.agr')
grace.view(file='noe.agr')

# Write the results.
write(run, file='results', dir=None, force=1)

# Save the program state.
state.save('save', force=1)
