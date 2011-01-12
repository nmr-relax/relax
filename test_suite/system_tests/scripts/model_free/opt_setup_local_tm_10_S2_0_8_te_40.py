"""Script for setting up the data pipe for testing optimisation.

The data set is:
    S2 = 0.970.
    te = 2048 ps.
    Rex = 0.149 s^-1.
"""

# Python module imports.
from os import sep
import sys

# relax module imports.
from status import Status; status = Status()


# Path of the files.
cdp.path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'local_tm_10_S2_0.8_te_40'

# Create the single residue.
residue.create(res_num=5, res_name='GLU')

# Setup other values.
value.set(1.02 * 1e-10, 'bond_length')
value.set(-172 * 1e-6, 'csa')
value.set('15N', 'heteronucleus')
value.set('1H', 'proton')

# Select the model-free model.
model_free.select_model(model='tm2')
