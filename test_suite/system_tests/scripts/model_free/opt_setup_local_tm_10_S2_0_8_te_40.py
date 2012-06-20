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

# Create the two spins.
spin.create(res_num=5, res_name='GLU', spin_name='N')
spin.create(res_num=5, res_name='GLU', spin_name='H')

# Define the magnetic dipole-dipole relaxation interaction.
dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
dipole_pair.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)

# Define the chemical shift relaxation interaction.
value.set(-172 * 1e-6, 'csa')

# Set the spin information.
spin.isotope('15N', spin_id='@N')
spin.isotope('1H', spin_id='@H')

# Select the model-free model.
model_free.select_model(model='tm2')
