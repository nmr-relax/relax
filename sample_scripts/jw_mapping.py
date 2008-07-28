# Script for reduced spectral density mapping.

# Create the run.
name = 'jw'
pipe.create(name, 'jw')

# Nuclei type
value.set('15N', 'heteronucleus')

# Load the sequence.
sequence.read(name, 'noe.600.out')

# Load the relaxation data.
relax_data.read(name, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
relax_data.read(name, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
relax_data.read(name, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')

# Set the bond length and CSA values.
value.set(name, 1.02 * 1e-10, 'bond_length')
value.set(name, -172 * 1e-6, 'csa')

# Select the frequency.
jw_mapping.set_frq(name, frq=600.0 * 1e6)

# Reduced spectral density mapping.
calc(name)

# Monte Carlo simulations.
monte_carlo.setup(name, number=500)
monte_carlo.create_data(name)
calc(name)
monte_carlo.error_analysis(name)

# Create grace files.
grace.write(name, y_data_type='j0', file='j0.agr', force=True)
grace.write(name, y_data_type='jwx', file='jwx.agr', force=True)
grace.write(name, y_data_type='jwh', file='jwh.agr', force=True)

# View the grace files.
grace.view(file='j0.agr')
grace.view(file='jwx.agr')
grace.view(file='jwh.agr')

# Finish.
results.write(file='results', force=True)
state.save('save', force=True)
