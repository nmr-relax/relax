# Script for mapping the model-free space.
load.sequence('noe.500.out')
load.relax_data('R1', '600', 600.0 * 1e6, 'r1.600.out')
load.relax_data('R2', '600', 600.0 * 1e6, 'r2.600.out')
load.relax_data('NOE', '600', 600.0 * 1e6, 'noe.600.out')
load.relax_data('R1', '500', 500.0 * 1e6, 'r1.500.out')
load.relax_data('R2', '500', 500.0 * 1e6, 'r2.500.out')
load.relax_data('NOE', '500', 500.0 * 1e6, 'noe.500.out')
model_selection.set('AIC')
value.set('bond_length', 1.02 * 1e-10)
value.set('csa', -160 * 1e-6)
diffusion_tensor('iso', 1e-8)
name = 'm5'
model.select_mf(name)

# Map data.
inc = 20
from math import pi
if name == 'm4':
    lower = [0.0, 0, 0]
    upper = [1, 200e-9, 0.2 / (2.0 * pi * 600000000.0)**2]
    swap = None
    point = [0.931, 8192e-12, 0.0 / (2.0 * pi * 600000000.0)**2]
elif name == 'm5':
    lower = [0.0, 0.0, 0]
    upper = [1.0, 0.01, 100e-12]
    swap = [0, 2, 1]
    point = [1.000, 0.00098352809884949435, 0.10105544919387284*1e-12]
else:
    lower = None
    upper = None
    swap = None
    point = None
map(name, res_num=0, inc=inc, lower=lower, upper=upper, swap=swap, point=point)
dx()
