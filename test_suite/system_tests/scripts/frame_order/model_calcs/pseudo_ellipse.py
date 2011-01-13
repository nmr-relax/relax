# Script for checking the pseudo-ellipse frame order model.

# Python module imports.
from numpy import array, float64
from os import sep

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from maths_fns.rotation_matrix import R_to_euler_zyz
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

# The frame order matrix eigenframe.
EIG_FRAME = array([[ 2, -1,  2],
                   [ 2,  2, -1],
                   [-1,  2,  2]], float64) / 3.0
a, b, g = R_to_euler_zyz(EIG_FRAME)

# Load the tensors.
script(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'tensors'+sep+'pseudo_ellipse_out_of_frame_theta_x_tensors_beta112_5.py')

# Data stores.
ds.chi2 = []
ds.angles = []

# Loop over the cones.
for i in range(INC):
    # Switch data pipes.
    ds.angles.append(get_angle(i, incs=INC, deg=True))
    pipe.switch('cone_%s_deg' % ds.angles[-1])

    # Data init.
    cdp.ave_pos_alpha  = cdp.ave_pos_alpha2  = 0.0
    cdp.ave_pos_beta   = cdp.ave_pos_beta2   = 112.5 / 360.0 * 2.0 * pi
    cdp.ave_pos_gamma  = cdp.ave_pos_gamma2  = 0.0
    cdp.eigen_alpha    = cdp.eigen_alpha2    = a
    cdp.eigen_beta     = cdp.eigen_beta2     = b
    cdp.eigen_gamma    = cdp.eigen_gamma2    = g
    cdp.cone_theta_x   = cdp.cone_theta_x2   = get_angle(i, incs=INC, deg=False)
    cdp.cone_theta_y   = cdp.cone_theta_y2   = 3.0 * pi / 8.0
    cdp.cone_sigma_max = cdp.cone_sigma_max2 = pi / 6.0

    # Select the Frame Order model.
    frame_order.select_model(model='pseudo-ellipse')

    # Set the reference domain.
    frame_order.ref_domain('full')

    # Calculate the chi2.
    calc()
    #cdp.chi2b = cdp.chi2
    #minimise('simplex')
    ds.chi2.append(cdp.chi2)

# Save the program state.
#state.save("pseudo_ellipse", force=True)

# Chi2 print out.
print "\n\n"
for i in range(INC):
    print("Cone %3i deg, chi2: %s" % (ds.angles[i], ds.chi2[i]))
