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

models = ['m1', 'm2', 'm3', 'm4', 'm5']
for i in range(len(models)):
    model.select_mf(models[i])
    grid_search(models[i], inc=11)
    minimise('newton', model=models[i])
    write(model=models[i], file='results', force=1)
    state.save('save', force=1)

state.save('save', force=1)
