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
name = 'm5'
model.select_mf(name)

# Fixed value.
fixed(name, [ 0.6,  1.0,  5.0*1e-10 ])
#from math import pi
#fixed(name, [ 0.95,  10.0*1e-9, 0.0 / (2.0 * pi * 600000000.0)**2 ])
#fixed(name, [ 1.00,  0.0*1e-12, 0.0 ])

# Grid search.
#grid_search(name, inc=11, constraints=0)
#write(model=name, file='grid_con_newton', force=1)

# Minimise.
#minimise('lm', model=name, constraints=0)
minimise('lm', model=name)
#write(model=name, file='results_con_newton', force=1)

state.save('save', force=1)
