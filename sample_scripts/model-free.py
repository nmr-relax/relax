# Script for model-free analysis.

# Load the sequence.
read.sequence('noe.500.out')

# Nuclei type
nuclei('N')

# Create the run.
name = 'm8'
create_run(name, 'mf')

# Load a PDB file.
#pdb('example.pdb')
#vectors()

# Load the relaxation data.
read.relax_data(name, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
read.relax_data(name, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
read.relax_data(name, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
read.relax_data(name, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
read.relax_data(name, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
read.relax_data(name, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

# Setup other values.
diffusion_tensor(name, 1e-8, fixed=1)
#diffusion_tensor(name, (1e-8, 1.0, 60, 290), param_types=1, axial_type='oblate', fixed=1)
#diffusion_tensor(name, (1.340e7, 1.516e7, 1.691e7, -82.027, -80.573, 65.568), fixed=0)
value.set(name, 'bond_length', 1.02 * 1e-10)
value.set(name, 'csa', -160 * 1e-6)

# Select the model-free model.
model.select_mf(run=name, model=name)
#model.create_mf(run=name, model=name, equation='mf_ext2', params=['S2f', 'S2s', 'ts'])

#select.res(num=4574)
# Fixed value.
#from math import pi
#set(name, [ 0.97, 2.048*1e-9, 0.149 / (2.0 * pi * 600000000.0)**2 ])
#set(name, [ 6.00000000e-01, 5.00000000e-01, 1.00000000e-9])
#set(name)
#fix(name, 'all_res')

# Grid search.
grid_search(name, inc=7, constraints=1, print_flag=1)

# Minimise.
#minimise('newton', run=name, constraints=1, max_iter=500)
#minimise('newton', run=name, constraints=1, print_flag=20, max_iter=0)
minimise('simplex', run=name, constraints=1)
#minimise('newton', run=name)

# Finish.
write(run=name, file='results', force=1)
state.save('save', force=1)
