# Script for checking the free rotor frame order model.

# Python module imports.
from os import sep

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Load the tensors.
self._execute_uf(uf_name='script', file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'tensors'+sep+'free_rotor_in_frame_rot_tensors.py')

# Data init.
cdp.ave_pos_beta = 0.5
cdp.ave_pos_gamma = 0.2
cdp.axis_theta  = 0.0
cdp.axis_phi = 0.0

# Select the Frame Order model.
self._execute_uf(uf_name='frame_order.select_model', model='free rotor')

# Set the reference domain.
self._execute_uf(uf_name='frame_order.ref_domain', ref='full')

# Calculate the chi2.
self._execute_uf(uf_name='calc')
#cdp.chi2b = cdp.chi2
#self._execute_uf(uf_name='minimise', min_algor='simplex')
ds.chi2 = cdp.chi2

# Save the program state.
#self._execute_uf(uf_name='state.save', state="free_rotor_eigenframe", force=True)

# Chi2 printout.
print("\n\n")
print("Chi2: %s" % cdp.chi2)
