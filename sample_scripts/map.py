# Script for mapping the model-free space.

# Load the sequence.
read.sequence('noe.500.out')

# Nuclei type
nuclei('N')

# Set the run name (also the name of a preset model-free model).
name = 'tm2'
create_run(name, 'mf')

# Load the relaxation data.
read.relax_data(name, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
read.relax_data(name, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
read.relax_data(name, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
read.relax_data(name, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
read.relax_data(name, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
read.relax_data(name, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

# Setup other values.
diffusion_tensor(name, 1e-8)
value.set(name, 1.02 * 1e-10, 'bond_length')
value.set(name, -170 * 1e-6, 'csa')

# Select the model-free model.
model.select_mf(run=name, model=name)
#model.create_mf(name, name, 'mf_ext2', ['S2f', 'S2s', 'ts'])

# Map data.
inc = 20
from math import pi
if name == 'x4':
    lower = [0, 0, 0]
    upper = [0.6, 1000e-12, 3.0 / (2.0 * pi * 600000000.0)**2]
    swap = None
    point = [0.263, 526.32e-12, 1.053 / (2.0 * pi * 600000000.0)**2]
elif name == 'x5':
    lower = [0.5, 0.5, 0]
    upper = [1.0, 1.0, 300e-12]
    swap = [0, 2, 1]
    point = [0.622, 0.555446, 281.74*1e-12]
else:
    lower = None
    upper = None
    swap = None
    point = None
map(name, res_num=5, inc=inc, lower=lower, upper=upper, swap=swap, point=point)
dx()
