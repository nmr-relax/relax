# Script for model-free analysis.

# Load the sequence.
read.sequence('noe.500.out')

# Set the run name (also the name of a preset model-free model).
name = 'm6'

# Load the relaxation data.
read.relax_data(name, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
read.relax_data(name, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
read.relax_data(name, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
read.relax_data(name, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
read.relax_data(name, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
read.relax_data(name, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

# Setup other values.
diffusion_tensor(name, 'iso', 1e-8)
value.set(name, 'bond_length', 1.02 * 1e-10)
value.set(name, 'csa', -160 * 1e-6)

# Select the model-free model.
model.select_mf(run=name, model=name)

# Fixed value.
#from math import pi
#fixed(name, [ 0.95, 10.0*1e-9, 0.0 / (2.0 * pi * 600000000.0)**2 ])
#fixed(name, [ 6.00000000e-01, 0.00000000e+00, 5.00000000e-01, 1.00000000e-9])

# Grid search.
grid_search(name, inc=11)

# Minimise.
#minimise('newton', 'gmw', run=name, constraints=0, max_iter=500)
#minimise('newton', 'gmw', run=name, constraints=0, print_flag=20, max_iter=0)
minimise('newton', run=name, print_flag=1)

# Finish.
write(run=name, file='results', force=1)
state.save('save', force=1)
