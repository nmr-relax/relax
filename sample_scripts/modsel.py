# Script for model-free analysis.
read.sequence('noe.500.out')
read.rx_data('R1', '600', 600.0 * 1e6, 'r1.600.out')
read.rx_data('R2', '600', 600.0 * 1e6, 'r2.600.out')
read.rx_data('NOE', '600', 600.0 * 1e6, 'noe.600.out')
read.rx_data('R1', '500', 500.0 * 1e6, 'r1.500.out')
read.rx_data('R2', '500', 500.0 * 1e6, 'r2.500.out')
read.rx_data('NOE', '500', 500.0 * 1e6, 'noe.500.out')
diffusion_tensor('iso', 1e-8)

runs = ['m1', 'm2', 'm3', 'm4', 'm5']
for i in range(len(runs)):
    value.set(runs[i], 'bond_length', 1.02 * 1e-10)
    value.set(runs[i], 'csa', -160 * 1e-6)
    model.select_mf(runs[i], runs[i])
    grid_search(runs[i], inc=11)
    minimise('newton', run=runs[i])
    write(run=runs[i], file='results', force=1)
    state.save('save', force=1)

state.save('save', force=1)
