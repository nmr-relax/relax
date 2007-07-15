# Script for consistency testing.

# Create the run.
name = 'consistency'
run.create(name, 'ct')

# Nuclei type
nuclei('N')

# Load the sequence.
sequence.read(name, 'noe.600.out')

# Load the relaxation data.
relax_data.read(name, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
relax_data.read(name, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
relax_data.read(name, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')

# Set the bond length and CSA values.
value.set(name, 1.02 * 1e-10, 'bond_length')
value.set(name, -172 * 1e-6, 'csa')

# Set the angle between the 15N-1H vector and the principal axis of the 15N chemical shift tensor
value.set(name, 15.7, 'orientation')

# Set the approximate correlation time.
value.set(name, 13 * 1e-9, 'tc')

# Set the frequency.
consistency_tests.set_frq(name, frq=600.0 * 1e6)

# Consistency tests.
calc(name)

# Monte Carlo simulations.
monte_carlo.setup(name, number=500)
monte_carlo.create_data(name)
calc(name)
monte_carlo.error_analysis(name)

# Create grace files.
grace.write(name, y_data_type='j0', file='j0.agr', force=1)
grace.write(name, y_data_type='f_eta', file='f_eta.agr', force=1)
grace.write(name, y_data_type='f_r2', file='f_r2.agr', force=1)

# View the grace files.
grace.view(file='j0.agr')
grace.view(file='f_eta.agr')
grace.view(file='f_r2.agr')

# Finish.
results.write(run=name, file='results', force=1)
state.save('save', force=1)
