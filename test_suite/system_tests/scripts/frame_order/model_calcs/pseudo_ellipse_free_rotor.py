# Script for checking the free rotor pseudo-ellipse frame order model.

# Python module imports.
from numpy import array, float64
from numpy.linalg import norm
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
EIG_FRAME = array([[ 2, -1,  2],
                   [ 2,  2, -1],
                   [-1,  2,  2]], float64) / 3.0
a, b, g = R_to_euler_zyz(EIG_FRAME)

files = ['pseudo_ellipse_free_rotor_in_frame_theta_y_tensors_beta0_0.py', 'pseudo_ellipse_free_rotor_out_of_frame_theta_x_tensors_beta22_5.py']
params = ['ave_pos_alpha', 'ave_pos_beta', 'ave_pos_gamma', 'eigen_alpha', 'eigen_beta', 'eigen_gamma', 'cone_theta_x', 'cone_theta_y']
ave_pos_alpha  = [0.0,              0.0                       ]
ave_pos_beta   = [0.0,              22.5 / 360.0 * 2.0 * pi   ]
ave_pos_gamma  = [0.0,              0.0                       ]
eigen_alpha    = [0.0,              a                         ]
eigen_beta     = [0.0,              b                         ]
eigen_gamma    = [0.0,              g                         ]
cone_theta_x   = [pi / 4.0,         'var'                     ]
cone_theta_y   = ['var',            3.0 * pi / 8.0            ]

# Data stores.
chi2 = []

# Loop over the different data sets.
for round in range(len(files)):
    # Reset relax.
    reset()

    # Load the tensors.
    script(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'tensors'+sep+files[round])

    # New set of chi2 values.
    chi2.append([])

    # Loop over the cones.
    for i in range(INC):
        # Switch data pipes.
        pipe.switch('cone_%s_deg' % get_angle(i, incs=INC, deg=True))

        # Data init.
        for j in range(len(params)):
            # The value.
            val = globals()[params[j]][round]

            # The incremented angle.
            if val == 'var':
                val = get_angle(i, incs=INC, deg=False)

            # Set the parameter name, storing an original copy for optimisation comparison.
            setattr(cdp, params[j], val)
            setattr(cdp, 'orig_' + params[j], val)

        # Select the Frame Order model.
        frame_order.select_model(model='pseudo-ellipse, free rotor')

        # Set the reference domain.
        frame_order.ref_domain('full')

        # Calculate the chi2.
        calc()
        #cdp.chi2b = cdp.chi2
        #minimise('simplex')
        chi2[round].append(cdp.chi2)

    # Save the program state.
    #state.save("pseudo_ellipse_free_rotor%s" % round, force=True)

# Chi2 print out.
ds.chi2 = chi2
print "\n\n"
for round in range(len(files)):
    print "\n\nFile: %s\n" % files[round]
    for i in range(INC):
        print("Cone %3i deg, chi2: %s" % (get_angle(i, incs=INC, deg=True), chi2[round][i]))
