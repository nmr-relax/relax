# Script for checking the free rotor frame order model.

# Python module imports.
import __main__
from numpy import array, float64
from os import sep

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from maths_fns.coord_transform import cartesian_to_spherical


# Generate 3 orthogonal vectors.
vect_z = array([2, 1, 3], float64)
r, theta, phi = cartesian_to_spherical(vect_z)

# Load the tensors.
execfile(__main__.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'tensors'+sep+'free_rotor_axis2_1_3_rot_tensors.py')

# Data init.
cdp.ave_pos_beta = 0.5
cdp.ave_pos_gamma = 0.2
cdp.axis_theta  = theta
cdp.axis_phi = phi

# Select the Frame Order model.
frame_order.select_model(model='free rotor')

# Set the reference domain.
frame_order.ref_domain('full')

# Calculate the chi2.
calc()
#cdp.chi2b = cdp.chi2
#minimise('simplex')
ds.chi2 = cdp.chi2

# Save the program state.
#state.save("free_rotor", force=True)

# Chi2 print out.
print "\n\n"
print("Chi2: %s" % cdp.chi2)
