# Script for checking the free rotor isotropic cone frame order model.

# Python module imports.
from numpy import array, float64
from numpy.linalg import norm
from os import sep

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from maths_fns.coord_transform import cartesian_to_spherical
from maths_fns.order_parameters import iso_cone_theta_to_S
from status import Status; status = Status()


def get_angle(index, incs=None, deg=False):
    """Return the angle corresponding to the incrementation index."""

    # The angle of one increment.
    inc_angle = pi / incs

    # The angle of the increment.
    angle = inc_angle * (index+1)

    # Return.
    if deg:
        return angle / (2*pi) * 360
    else:
        return angle


# Init.
INC = 18

# Generate 3 orthogonal vectors.
vect_z = array([2, 1, 3], float64)
r, theta, phi = cartesian_to_spherical(vect_z)

# Load the tensors.
self._execute_uf(uf_name='script', file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'tensors'+sep+'iso_cone_free_rotor_axis2_1_3_tensors_beta78_75.py')

# Data stores.
ds.chi2 = []
ds.angles = []

# Loop over the cones.
for i in range(INC):
    # Switch data pipes.
    ds.angles.append(get_angle(i, incs=INC, deg=True))
    self._execute_uf(uf_name='pipe.switch', pipe_name='cone_%s_deg' % ds.angles[-1])

    # Data init.
    cdp.ave_pos_beta  = 78.75 / 360.0 * 2.0 * pi
    cdp.ave_pos_gamma = 0.0
    cdp.axis_theta  = theta
    cdp.axis_phi = phi
    cdp.cone_s1 = iso_cone_theta_to_S(get_angle(i, incs=INC, deg=False))

    # Select the Frame Order model.
    self._execute_uf(uf_name='frame_order.select_model', model='iso cone, free rotor')

    # Set the reference domain.
    self._execute_uf(uf_name='frame_order.ref_domain', ref='full')

    # Calculate the chi2.
    self._execute_uf(uf_name='calc')
    #cdp.chi2b = cdp.chi2
    #self._execute_uf(uf_name='minimise', min_algor='simplex')
    ds.chi2.append(cdp.chi2)

# Save the program state.
#self._execute_uf(uf_name='state.save', state="iso_cone_free_rotor", force=True)

# Chi2 printout.
print "\n\n"
for i in range(INC):
    print("Cone %3i deg, chi2: %s" % (ds.angles[i], ds.chi2[i]))
