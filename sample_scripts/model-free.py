# Script for model-free analysis.
load.sequence('noe.500.out')
load.relax_data('R1', '600', 600.0 * 1e6, 'r1.600.out')
load.relax_data('R2', '600', 600.0 * 1e6, 'r2.600.out')
load.relax_data('NOE', '600', 600.0 * 1e6, 'noe.600.out')
load.relax_data('R1', '500', 500.0 * 1e6, 'r1.500.out')
load.relax_data('R2', '500', 500.0 * 1e6, 'r2.500.out')
load.relax_data('NOE', '500', 500.0 * 1e6, 'noe.500.out')
value.set('bond_length', 1.02 * 1e-10)
value.set('csa', -160 * 1e-6)
diffusion_tensor('iso', 1e-8)
name = 'tm5'
model.select_mf(name)
#model.create_mf(name, 'mf_ext2', ['S2f', 'S2s', 'ts'])

# Fixed value.
#from math import pi
#fixed(name, [ 1.0, 0.00098352809884949435, 0.10105544919387284*1e-12 ])
#fixed(name, [ 0.95, 10.0*1e-9, 0.0 / (2.0 * pi * 600000000.0)**2 ])
#write(model=name, file='results_fixed', force=1)

# Grid search.
state.save('save', force=1)
grid_search(name, inc=11)
#write(model=name, file='results_grid', force=1)

# Minimise.
#minimise('newton', model=name, constraints=0)
minimise('newton', model=name)
write(model=name, file='results', force=1)

state.save('save', force=1)
