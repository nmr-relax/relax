"""This system test catches 2 bugs submitted by Chris Brosey.

The bugs include:
    - Bug #12582 (https://gna.org/bugs/?12582).
    - Bug #12591 (https://gna.org/bugs/?12591).
    - Bug #12607 (https://gna.org/bugs/?12607).
"""

# Python module imports.
from os import sep
import sys

# relax module imports.
from status import Status; status = Status()


# Path of the files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

# Loop over the models.
for name in ['tm0', 'tm1']:
    # Setup.
    pipe.create(pipe_name=name, pipe_type='mf')
    sequence.read(file='noe.500.out', dir=path, mol_name_col=None, res_num_col=1, res_name_col=2, spin_num_col=None, spin_name_col=None, sep=None)
    relax_data.read(ri_label='R1', frq_label='500', frq=500208000.0, file='r1.500.out', dir=path, mol_name_col=None, res_num_col=1, res_name_col=2, spin_num_col=None, spin_name_col=None, data_col=3, error_col=4, sep=None)
    relax_data.read(ri_label='R2', frq_label='500', frq=500208000.0, file='r2.500.out', dir=path, mol_name_col=None, res_num_col=1, res_name_col=2, spin_num_col=None, spin_name_col=None, data_col=3, error_col=4, sep=None)
    relax_data.read(ri_label='NOE', frq_label='500', frq=500208000.0, file='noe.500.out', dir=path, mol_name_col=None, res_num_col=1, res_name_col=2, spin_num_col=None, spin_name_col=None, data_col=3, error_col=4, sep=None)
    value.set(val=1.0200000000000001e-10, param='bond_length', spin_id=None)
    value.set(val=-0.00017199999999999998, param='csa', spin_id=None)
    value.set(val='15N', param='heteronucleus', spin_id=None)
    value.set(val='1H', param='proton', spin_id=None)
    model_free.select_model(model=name, spin_id=None)

    # Optimisation.
    grid_search(lower=None, upper=None, inc=11, constraints=True, verbosity=1)
    minimise('newton', func_tol=1e-25, max_iterations=10000000, constraints=True, scaling=True, verbosity=1)

    # Results writing.
    results.write(file='devnull', force=True, compress_type=1)

# Model selection.
sequence.display()
eliminate(function=None, args=None)
model_selection(method='AIC', modsel_pipe='aic', pipes=['tm0', 'tm1'])



# Catch bug #12607 (https://gna.org/bugs/?12607).
#################################################

model_free.remove_tm(spin_id=None)
diffusion_tensor.init(params=1e-08, time_scale=1.0, d_scale=1.0, angle_units='deg', param_types=0, spheroid_type=None, fixed=False)
fix(element='all_spins', fixed=True)
grid_search(lower=None, upper=None, inc=11, constraints=True, verbosity=1)
