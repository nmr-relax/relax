# Script for mapping the model-free space.
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
#model.select_mf(run=name, model=name)
model.create_mf(name, name, 'mf_ext2', ['S2f', 'S2s', 'ts'])

# Map data.
inc = 10
from math import pi
if name == 'm4':
    lower = [0.0, 0, 0]
    upper = [1, 200e-9, 0.2 / (2.0 * pi * 600000000.0)**2]
    swap = None
    point = [0.931, 8192e-12, 0.0 / (2.0 * pi * 600000000.0)**2]
elif name == 'm5':
    lower = [0.5, 0.5, 0]
    upper = [1.0, 1.0, 1000e-12]
    swap = [0, 2, 1]
    point = [0.952, 0.582, 32*1e-12]
else:
    lower = None
    upper = None
    swap = None
    point = None
map(name, res_num=1, inc=inc, lower=lower, upper=upper, swap=swap, point=point)
dx()
