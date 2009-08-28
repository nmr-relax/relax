# Script for reduced spectral density mapping.

# Create the data pipe.
pipe.create('my_protein', 'jw')

# Load the sequence.
sequence.read('noe.600.out')

# Load the relaxation data.
relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out')
relax_data.read('R2', '600', 600.0 * 1e6, 'r2.600.out')
relax_data.read('NOE', '600', 600.0 * 1e6, 'noe.600.out')

# Set the nuclei types.
value.set('15N', 'heteronucleus')
value.set('1H', 'proton')

# Set the bond length and CSA values.
value.set(1.02 * 1e-10, 'bond_length')
value.set(-172 * 1e-6, 'csa')

# Select the frequency.
jw_mapping.set_frq(frq=600.0 * 1e6)

# Reduced spectral density mapping.
calc()

# Monte Carlo simulations (well, bootstrapping as this is a calculation and not a fit!).
monte_carlo.setup(number=500)
monte_carlo.create_data()
calc()
monte_carlo.error_analysis()

# Create grace files.
grace.write(y_data_type='j0', file='j0.agr', force=True)
grace.write(y_data_type='jwx', file='jwx.agr', force=True)
grace.write(y_data_type='jwh', file='jwh.agr', force=True)

# View the grace files.
grace.view(file='j0.agr')
grace.view(file='jwx.agr')
grace.view(file='jwh.agr')

# Finish.
results.write(file='results', force=True)
state.save('save', force=True)
