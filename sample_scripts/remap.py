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
        s2s = values[1]/values[0]

    # ts.
    ts = values[2]

    #print "{S2f = " + `s2f` + ", S2s = " + `s2s` + ", ts = " + `ts` + "}"
    return array([s2f, s2s, ts], Float64)


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
lower = [0.0, 0.0, 0]
upper = [1.0, 1.0, 2000e-12]
swap = [0, 2, 1]
point = [0.952, 0.582, 32.0e-12]
point = [point[0], point[0]*point[1], point[2]]

map(name, inc=inc, lower=lower, upper=upper, swap=swap, file='remap', point=point, remap=remap, labels=['S2f', 'S2', 'ts'])
dx(file='remap')
