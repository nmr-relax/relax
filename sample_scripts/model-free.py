# Script for model-free analysis.
read.sequence('noe.500.out')
read.rx_data('R1', '600', 600.0 * 1e6, 'r1.600.out')
read.rx_data('R2', '600', 600.0 * 1e6, 'r2.600.out')
read.rx_data('NOE', '600', 600.0 * 1e6, 'noe.600.out')
read.rx_data('R1', '500', 500.0 * 1e6, 'r1.500.out')
read.rx_data('R2', '500', 500.0 * 1e6, 'r2.500.out')
read.rx_data('NOE', '500', 500.0 * 1e6, 'noe.500.out')
diffusion_tensor('iso', 1e-8)
name = 'm5'
value.set(name, 'bond_length', 1.02 * 1e-10)
value.set(name, 'csa', -160 * 1e-6)
model.select_mf(run=name, model=name)
#model.create_mf(name, name, 'mf_ext2', ['S2f', 'S2s', 'ts'])

# Fixed value.
#from math import pi
#fixed(name, [ 1.0, 0.00098352809884949435, 0.10105544919387284*1e-12 ])
#fixed(name, [ 0.95, 10.0*1e-9, 0.0 / (2.0 * pi * 600000000.0)**2 ])
#fixed(name, [ 10000*1e-12, 0.952, 0.0, 0.55406, 32*1e-12 ])
#fixed(name, [ 10000*1e-12, 0.6, 0.0, 0.5, 1000*1e-12 ])
#write(run=name, file='results_fixed', force=1)

# Grid search.
grid_search(name, inc=11)
#write(run=name, file='results_grid', force=1)

# Minimise.
#minimise('newton', run=name, constraints=0, max_iter=0, print_flag=10)
minimise('newton', run=name)
write(run=name, file='results', force=1)

state.save('save', force=1)
