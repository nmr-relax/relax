# Script for mapping the model-free space.

from Numeric import Float64, array


def remap(values):
    """Remapping function."""

    # S2f.
    s2f = values[0]

    # S2s.
    if values[0] == 0.0:
        s2s = 1e99
    else:
        s2s = values[1]*values[0]

    # ts.
    ts = values[2]

    return array([s2f, s2s, ts], Float64)


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
model.select_mf(name, name)

# Map data.
inc = 100
lower = [0.5, 0.5, 0]
upper = [1.0, 1.0, 300e-12]
swap = [0, 2, 1]
point = [0.952, 0.582, 32.0e-12]
point = [point[0], point[0]*point[1], point[2]]

map(name, res_num=1, inc=inc, lower=lower, upper=upper, swap=swap, file='remap', point=point, remap=remap, labels=['S2f', 'S2s', 'ts'])
dx(file='remap')
