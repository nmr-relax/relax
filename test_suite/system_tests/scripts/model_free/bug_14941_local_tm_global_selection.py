"""This system test catches the local tm global model selection bug submitted by Mikaela Stewart (mikaela dot stewart att gmail dot com).

The bug is:
    - Bug #14941 (https://gna.org/bugs/?14941).
"""

# Python module imports.
import __main__
from os import sep
import sys


# Path of the files.
path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'bug_14941_local_tm_global_selection'

# Local tm data.
pipe.create(pipe_name='local_tm', pipe_type='mf')
results.read(file='local_tm_trunc', dir=path)

# Sphere data.
pipe.create(pipe_name='sphere', pipe_type='mf')
results.read(file='sphere_trunc', dir=path)

# Model selection.
model_selection(method='AIC', modsel_pipe='final', pipes=['local_tm', 'sphere'])
results.write(file='devnull', dir=None, compress_type=1, force=True)

# Monte Carlo simulation setup.
monte_carlo.setup(number=200)
monte_carlo.create_data(method='back_calc')
monte_carlo.initial_values()

