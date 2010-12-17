# Script for checking the free rotor frame order model.

# Python module imports.
import __main__
from os import sep

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


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

# Load the tensors.
script(__main__.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'tensors'+sep+'rotor_in_frame_tensors_beta22_5.py')

# Data stores.
ds.chi2 = []
ds.angles = []

# Loop over the cones.
for i in range(INC):
    # Switch data pipes.
    ds.angles.append(get_angle(i, incs=INC, deg=True))
    pipe.switch('cone_%s_deg' % ds.angles[-1])

    # Data init.
    cdp.ave_pos_beta   = cdp.ave_pos_beta2   = 22.5 / 360.0 * 2.0 * pi
    cdp.cone_sigma_max = cdp.cone_sigma_max2 = get_angle(i, incs=INC, deg=False)

    # Select the Frame Order model.
    frame_order.select_model(model='rotor')

    # Set the reference domain.
    frame_order.ref_domain('full')

    # Calculate the chi2.
    calc()
    #cdp.chi2b = cdp.chi2
    #minimise('simplex')
    ds.chi2.append(cdp.chi2)

# Save the program state.
#state.save("rotor_eigenframe", force=True)

# Chi2 print out.
print "\n\n"
for i in range(INC):
    print("Cone %3i deg, chi2: %s" % (ds.angles[i], ds.chi2[i]))
