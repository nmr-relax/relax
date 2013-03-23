# Script for checking the free rotor frame order model.

# Python module imports.
from numpy import array, float64
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from lib.geometry.coord_transform import cartesian_to_spherical
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
vect_z = array([2, -1, 2], float64)
r, theta, phi = cartesian_to_spherical(vect_z)

# Load the tensors.
self._execute_uf(uf_name='script', file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'tensors'+sep+'rotor_out_of_frame_tensors_beta123_75.py')

# Data stores.
ds.chi2 = []
ds.angles = []

# Loop over the cones.
for i in range(INC):
    # Switch data pipes.
    ds.angles.append(get_angle(i, incs=INC, deg=True))
    self._execute_uf(uf_name='pipe.switch', pipe_name='cone_%.1f_deg' % ds.angles[-1])

    # Data init.
    cdp.ave_pos_beta   = cdp.ave_pos_beta2   = 123.75 / 360.0 * 2.0 * pi
    cdp.axis_theta    = cdp.axis_theta2    = theta
    cdp.axis_phi     = cdp.axis_phi2     = phi
    cdp.cone_sigma_max = cdp.cone_sigma_max2 = get_angle(i, incs=INC, deg=False)

    # Select the Frame Order model.
    self._execute_uf(uf_name='frame_order.select_model', model='rotor')

    # Set the reference domain.
    self._execute_uf(uf_name='frame_order.ref_domain', ref='full')

    # Calculate the chi2.
    self._execute_uf(uf_name='calc')
    #cdp.chi2b = cdp.chi2
    #self._execute_uf(uf_name='minimise', min_algor='simplex')
    ds.chi2.append(cdp.chi2)

# Save the program state.
#self._execute_uf(uf_name='state.save', state="rotor", force=True)

# Chi2 printout.
print("\n\n")
for i in range(INC):
    print("Cone %3i deg, chi2: %s" % (ds.angles[i], ds.chi2[i]))
