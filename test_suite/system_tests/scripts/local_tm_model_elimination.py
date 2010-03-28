"""Script for eliminating model tm4 with parameters {local_tm, S2, te, Rex} when tm > 50 ns."""

# Python module imports.
import __main__
from os import sep
import sys


# Read the sequence.
sequence.read(file='Ap4Aase.Noe.600', dir=__main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'relaxation_data'+sep, res_num_col=1, res_name_col=2)

# Select the model.
model_free.select_model(model='tm4')

# Set a local tm value
value.set(51 * 1e-9, 'local_tm', spin_id=":15")

# Model elimination.
eliminate()
