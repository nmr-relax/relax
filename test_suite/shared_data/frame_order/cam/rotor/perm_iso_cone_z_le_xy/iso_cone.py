# Optimise all 3 iso cone permutations for the CaM rotor synthetic frame order data.
# These 3 solutions should mimic the rotor solution.

# Python module imports.
from numpy import float64, zeros
import sys

# relax module imports.
from lib.geometry.coord_transform import spherical_to_cartesian
from lib.text.sectioning import section


# The real rotor parameter values.
AVE_POS_X, AVE_POS_Y, AVE_POS_Z = [ -21.269217407269576,   -3.122610661328414,   -2.400652421655998]
AVE_POS_ALPHA, AVE_POS_BETA, AVE_POS_GAMMA = [5.623469076122531, 0.435439405668396, 5.081265529106499]
AXIS_THETA = 0.9600799785953431
AXIS_PHI = 4.0322755062196229
CONE_SIGMA_MAX = 30.0 / 360.0 * 2.0 * pi

# Reconstruct the rotation axis.
AXIS = zeros(3, float64)
spherical_to_cartesian([1, AXIS_THETA, AXIS_PHI], AXIS)

# Printout.
print("Torsion angle: %s" % CONE_SIGMA_MAX)
print("Rotation axis: %s" % AXIS)

# Load the optimised rotor state for creating the iso cone data pipes.
state.load(state='frame_order_true', dir='..')

# Set up the dynamic system.
value.set(param='ave_pos_x', val=AVE_POS_X)
value.set(param='ave_pos_y', val=AVE_POS_Y)
value.set(param='ave_pos_z', val=AVE_POS_Z)
value.set(param='ave_pos_alpha', val=AVE_POS_ALPHA)
value.set(param='ave_pos_beta', val=AVE_POS_BETA)
value.set(param='ave_pos_gamma', val=AVE_POS_GAMMA)
value.set(param='axis_theta', val=AXIS_THETA)
value.set(param='axis_phi', val=AXIS_PHI)

# Set the torsion angle to the rotor opening half-angle.
value.set(param='cone_sigma_max', val=CONE_SIGMA_MAX)

# Set the cone opening angle.
value.set(param='cone_theta', val=0.8)

# Fix the true pivot point.
frame_order.pivot([ 37.254, 0.5, 16.7465], fix=True)

# Change the model.
frame_order.select_model('iso cone')

# Loop over the 2 permutations.
pipe_name = 'iso cone'
tag = ''
for perm in [None, 'A']:
    # The original permutation.
    if perm == None:
        # Title printout.
        section(file=sys.stdout, text="Isotropic cone original permutation")

        # Create a new data base data pipe for the iso cone.
        pipe.copy(pipe_from='frame order', pipe_to='iso cone')
        pipe.switch(pipe_name='iso cone')

    # Operations for the 'A' and 'B' permutations.
    else:
        # Title printout.
        section(file=sys.stdout, text="Isotropic cone permutation %s" % perm)

        # The pipe name and tag.
        pipe_name = 'iso cone perm %s' % perm
        tag = '_perm_%s' % perm

        # Create a new data pipe.
        pipe.copy(pipe_from='frame order', pipe_to=pipe_name)
        pipe.switch(pipe_name=pipe_name)

        # Permute the axes.
        frame_order.permute_axes(permutation=perm)

    # Create a pre-optimisation PDB representation.
    frame_order.pdb_model(ave_pos=None, rep='fo_orig'+tag, dist=None, compress_type=2, force=True)

    # High precision optimisation.
    frame_order.num_int_pts(num=10000)
    minimise.execute('simplex', func_tol=1e-4)

    # Create the PDB representation.
    frame_order.pdb_model(ave_pos=None, rep='fo'+tag, dist=None, compress_type=2, force=True)

# Sanity check.
pipe.display()
