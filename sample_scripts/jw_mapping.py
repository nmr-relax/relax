# Script for reduced spectral density mapping.

# Create the run.
name = 'jw'
create_run(name, 'jw')

# Nuclei type
nuclei('N')

# Load the sequence.
sequence.read(name, 'noe.500.out')

# Load the relaxation data.
relax_data.read(name, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
relax_data.read(name, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
relax_data.read(name, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
relax_data.read(name, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
relax_data.read(name, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
relax_data.read(name, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

# Set the bond length and CSA values.
value.set(name, 1.02 * 1e-10, 'bond_length')
value.set(name, -160 * 1e-6, 'csa')

# Select the frequency.
jw_mapping.set_frq(name, frq=600.0 * 1e6)

# Reduced spectral density mapping.
calc(name)
