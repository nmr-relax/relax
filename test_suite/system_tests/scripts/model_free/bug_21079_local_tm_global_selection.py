"""This system test catches the local tm global model selection bug.

The bug is:
    - Bug #21079 (U{bug #21079<https://gna.org/bugs/?21079>}).
"""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Path of the files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'bug_21079_local_tm_global_selection'

# Load the state files.
pipes = ['local_tm', 'sphere']
files = ['local_tm_trunc', 'sphere_trunc']
for i in range(len(pipes)):
    pipe.create(pipes[i], 'mf')
    results.read(file=files[i], dir=path)

# Model selection.
model_selection(method='AIC', modsel_pipe='final', pipes=['local_tm', 'sphere'])

# Display the sequence data for a sanity check.
sequence.display()

# Monte Carlo simulations.
monte_carlo.setup(number=5)
monte_carlo.create_data(method='back_calc')
monte_carlo.initial_values()
minimise()
monte_carlo.error_analysis()
