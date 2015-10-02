###############################################################################
#                                                                             #
# Copyright (C) 2009-2015 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for all of the frame order specific user functions."""

# Python module imports.
from copy import deepcopy
from math import pi
from numpy import array, cross, float64, ones, transpose, zeros
from numpy.linalg import norm
from warnings import warn

# relax module imports.
from lib.arg_check import is_float_array
from lib.check_types import is_float
from lib.errors import RelaxError, RelaxFault
from lib.frame_order.simulation import brownian, uniform_distribution
from lib.frame_order.variables import MODEL_DOUBLE_ROTOR, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS, MODEL_LIST, MODEL_LIST_FREE_ROTORS, MODEL_LIST_ISO_CONE, MODEL_LIST_PSEUDO_ELLIPSE, MODEL_LIST_RESTRICTED_TORSION, MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_RIGID
from lib.geometry.coord_transform import cartesian_to_spherical, spherical_to_cartesian
from lib.geometry.rotations import euler_to_R_zyz, R_to_euler_zyz
from lib.io import open_write_file
from lib.warnings import RelaxWarning
from pipe_control import pipes
from specific_analyses.frame_order.checks import check_domain, check_model, check_parameters, check_pivot
from specific_analyses.frame_order.data import domain_moving, generate_pivot
from specific_analyses.frame_order.geometric import average_position, create_ave_pos, create_geometric_rep, generate_axis_system
from specific_analyses.frame_order.optimisation import count_sobol_points
from specific_analyses.frame_order.parameters import assemble_param_vector, update_model


def distribute(file="distribution.pdb.bz2", dir=None, atom_id=None, total=1000, max_rotations=100000, model=1, force=True):
    """Create a uniform distribution of structures for the frame order motions.

    @keyword file:          The PDB file for storing the frame order motional distribution.  The compression is determined automatically by the file extensions '*.pdb', '*.pdb.gz', and '*.pdb.bz2'.
    @type file:             str
    @keyword dir:           The directory name to place the file into.
    @type dir:              str or None
    @keyword atom_id:       The atom identification string to allow the distribution to be a subset of all atoms.
    @type atom_id:          None or str
    @keyword total:         The total number of states/model/structures in the distribution.
    @type total:            int
    @keyword max_rotations: The maximum number of rotations to generate the distribution from.  This prevents an execution for an infinite amount of time when a frame order amplitude parameter is close to zero so that the subset of all rotations within the distribution is close to zero.
    @type max_rotations:    int
    @keyword model:         Only one model from an analysed ensemble of structures can be used for the distribution, as the corresponding PDB file consists of one model per state.
    @type model:            int
    @keyword force:         A flag which, if set to True, will overwrite the any pre-existing file.
    @type force:            bool
    """

    # Printout.
    print("Uniform distribution of structures representing the frame order motions.")

    # Checks.
    check_pipe()
    check_model()
    check_domain()
    check_parameters()
    check_pivot()

    # Skip the rigid model.
    if cdp.model == MODEL_RIGID:
        print("Skipping the rigid model.")
        return

    # Open the output file.
    file = open_write_file(file_name=file, dir=dir, force=force)

    # The parameter values.
    values = assemble_param_vector()
    params = {}
    i = 0
    for name in cdp.params:
        params[name] = values[i]
        i += 1

    # The structure.
    structure = deepcopy(cdp.structure)
    if structure.num_models() > 1:
        structure.collapse_ensemble(model_num=model)

    # The pivot points.
    num_states = 1
    if cdp.model == MODEL_DOUBLE_ROTOR:
        num_states = 2
    pivot = zeros((num_states, 3), float64)
    for i in range(num_states):
        pivot[i] = generate_pivot(order=i+1, pdb_limit=True)

    # Shift to the average position.
    average_position(structure=structure, models=[None])

    # The motional eigenframe.
    frame = generate_axis_system()

    # Only work with a subset.
    if atom_id:
        # The inverted selection.
        selection = structure.selection(atom_id=atom_id, inv=True)

        # Delete the data.
        structure.delete(selection=selection, verbosity=0)

    # Create the distribution.
    uniform_distribution(file=file, model=cdp.model, structure=structure, parameters=params, eigenframe=frame, pivot=pivot, atom_id=domain_moving(), total=total, max_rotations=max_rotations)

    # Close the file.
    file.close()


def pdb_model(ave_pos="ave_pos", rep="frame_order", dir=None, compress_type=0, size=30.0, inc=36, model=1, force=False):
    """Create 3 different PDB files for representing the frame order dynamics of the system.

    @keyword ave_pos:       The file root for the average molecule structure.
    @type ave_pos:          str or None
    @keyword rep:           The file root of the PDB representation of the frame order dynamics to create.
    @type rep:              str or None
    @keyword dist:          The file root which will contain multiple models spanning the full dynamics distribution of the frame order model.
    @type dist:             str or None
    @keyword dir:           The name of the directory to place the PDB file into.
    @type dir:              str
    @keyword compress_type: The compression type.  The integer values correspond to the compression type: 0, no compression; 1, Bzip2 compression; 2, Gzip compression.
    @type compress_type:    int
    @keyword size:          The size of the geometric object in Angstroms.
    @type size:             float
    @keyword inc:           The number of increments for the filling of the cone objects.
    @type inc:              int
    @keyword model:      Only one model from an analysed ensemble can be used for the PDB representation of the Monte Carlo simulations, as these consists of one model per simulation.
    @type model:         int
    @keyword force:         Flag which if set to True will cause any pre-existing file to be overwritten.
    @type force:            bool
    """

    # Check that at least one PDB file name is given.
    if not ave_pos and not rep and not dist:
        raise RelaxError("Minimally one PDB file name must be supplied.")

    # Test if the current data pipe exists.
    check_pipe()

    # Create the average position structure.
    if ave_pos:
        create_ave_pos(file=ave_pos, dir=dir, compress_type=compress_type, model=model, force=force)

    # Nothing more to do for the rigid model.
    if cdp.model == MODEL_RIGID:
        return

    # Create the geometric representation.
    if rep:
        create_geometric_rep(file=rep, dir=dir, compress_type=compress_type, size=size, inc=inc, force=force)


def permute_axes(permutation='A'):
    """Permute the axes of the motional eigenframe to switch between local minima.

    @keyword permutation:   The permutation to use.  This can be either 'A' or 'B' to select between the 3 permutations, excluding the current combination.
    @type permutation:      str
    """

    # Check that the model is valid.
    allowed = MODEL_LIST_ISO_CONE + MODEL_LIST_PSEUDO_ELLIPSE
    if cdp.model not in allowed:
        raise RelaxError("The permutation of the motional eigenframe is only valid for the frame order models %s." % allowed)

    # Check that the model parameters are setup.
    if cdp.model in MODEL_LIST_ISO_CONE:
        if not hasattr(cdp, 'cone_theta') or not is_float(cdp.cone_theta):
            raise RelaxError("The parameter values are not set up.")
    else:
        if not hasattr(cdp, 'cone_theta_y') or not is_float(cdp.cone_theta_y):
            raise RelaxError("The parameter values are not set up.")

    # The iso cones only have one permutation.
    if cdp.model in MODEL_LIST_ISO_CONE and permutation == 'B':
        raise RelaxError("The isotropic cones only have one permutation.")

    # The angles.
    cone_sigma_max = 0.0
    if cdp.model in MODEL_LIST_RESTRICTED_TORSION:
        cone_sigma_max = cdp.cone_sigma_max
    elif cdp.model in MODEL_LIST_FREE_ROTORS:
        cone_sigma_max = pi
    if cdp.model in MODEL_LIST_ISO_CONE:
        angles = array([cdp.cone_theta, cdp.cone_theta, cone_sigma_max], float64)
    else:
        angles = array([cdp.cone_theta_x, cdp.cone_theta_y, cone_sigma_max], float64)
    x, y, z = angles

    # The axis system.
    axes = generate_axis_system()

    # Start printout for the isotropic cones.
    if cdp.model in MODEL_LIST_ISO_CONE:
        print("\nOriginal parameters:")
        print("%-20s %20.10f" % ("cone_theta", cdp.cone_theta))
        print("%-20s %20.10f" % ("cone_sigma_max", cone_sigma_max))
        print("%-20s %20.10f" % ("axis_theta", cdp.axis_theta))
        print("%-20s %20.10f" % ("axis_phi", cdp.axis_phi))
        print("%-20s\n%s" % ("cone axis", axes[:, 2]))
        print("%-20s\n%s" % ("full axis system", axes))
        print("\nPermutation '%s':" % permutation)

    # Start printout for the pseudo-ellipses.
    else:
        print("\nOriginal parameters:")
        print("%-20s %20.10f" % ("cone_theta_x", cdp.cone_theta_x))
        print("%-20s %20.10f" % ("cone_theta_y", cdp.cone_theta_y))
        print("%-20s %20.10f" % ("cone_sigma_max", cone_sigma_max))
        print("%-20s %20.10f" % ("eigen_alpha", cdp.eigen_alpha))
        print("%-20s %20.10f" % ("eigen_beta", cdp.eigen_beta))
        print("%-20s %20.10f" % ("eigen_gamma", cdp.eigen_gamma))
        print("%-20s\n%s" % ("eigenframe", axes))
        print("\nPermutation '%s':" % permutation)

    # The axis inversion structure.
    inv = ones(3, float64)

    # The starting condition x <= y <= z.
    if x <= y and y <= z:
        # Printout.
        print("%-20s %-20s" % ("Starting condition", "x <= y <= z"))

        # The cone angle and axes permutations.
        if permutation == 'A':
            perm_angles = [0, 2, 1]
            perm_axes   = [2, 1, 0]
            inv[perm_axes[2]] = -1.0
        else:
            perm_angles = [1, 2, 0]
            perm_axes   = [2, 0, 1]

    # The starting condition x <= z <= y.
    elif x <= z and z <= y:
        # Printout.
        print("%-20s %-20s" % ("Starting condition", "x <= z <= y"))

        # The cone angle and axes permutations.
        if permutation == 'A':
            perm_angles = [0, 2, 1]
            perm_axes   = [2, 1, 0]
            inv[perm_axes[2]] = -1.0
        else:
            perm_angles = [2, 1, 0]
            perm_axes   = [0, 2, 1]
            inv[perm_axes[2]] = -1.0

    # The starting condition z <= x <= y.
    elif z <= x  and x <= y:
        # Printout.
        print("%-20s %-20s" % ("Starting condition", "z <= x <= y"))

        # The cone angle and axes permutations.
        if permutation == 'A':
            perm_angles = [2, 0, 1]
            perm_axes   = [1, 2, 0]
        else:
            perm_angles = [2, 1, 0]
            perm_axes   = [0, 2, 1]
            inv[perm_axes[2]] = -1.0

    # Cannot be here.
    else:
        raise RelaxFault

    # Printout.
    print("%-20s %-20s" % ("Cone angle permutation", perm_angles))
    print("%-20s %-20s" % ("Axes permutation", perm_axes))

    # Permute the angles.
    if cdp.model in MODEL_LIST_ISO_CONE:
        cdp.cone_theta = (angles[perm_angles[0]] + angles[perm_angles[1]]) / 2.0
    else:
        cdp.cone_theta_x = angles[perm_angles[0]]
        cdp.cone_theta_y = angles[perm_angles[1]]
    if cdp.model in MODEL_LIST_RESTRICTED_TORSION:
        cdp.cone_sigma_max = angles[perm_angles[2]]
    elif cdp.model in MODEL_LIST_FREE_ROTORS:
        cdp.cone_sigma_max = pi

    # Permute the axes (iso cone).
    if cdp.model in MODEL_LIST_ISO_CONE:
        # Convert the y-axis to spherical coordinates (the x-axis would be ok too, or any vector in the x-y plane due to symmetry of the original permutation).
        axis_new = axes[:, 1]
        r, cdp.axis_theta, cdp.axis_phi = cartesian_to_spherical(axis_new)

    # Permute the axes (pseudo-ellipses).
    else:
        axes_new = transpose(array([inv[0]*axes[:, perm_axes[0]], inv[1]*axes[:, perm_axes[1]], inv[2]*axes[:, perm_axes[2]]], float64))

        # Convert the permuted frame to Euler angles and store them.
        cdp.eigen_alpha, cdp.eigen_beta, cdp.eigen_gamma = R_to_euler_zyz(axes_new)

    # End printout.
    if cdp.model in MODEL_LIST_ISO_CONE:
        print("\nPermuted parameters:")
        print("%-20s %20.10f" % ("cone_theta", cdp.cone_theta))
        if cdp.model == MODEL_ISO_CONE:
            print("%-20s %20.10f" % ("cone_sigma_max", cdp.cone_sigma_max))
        print("%-20s %20.10f" % ("axis_theta", cdp.axis_theta))
        print("%-20s %20.10f" % ("axis_phi", cdp.axis_phi))
        print("%-20s\n%s" % ("cone axis", axis_new))
    else:
        print("\nPermuted parameters:")
        print("%-20s %20.10f" % ("cone_theta_x", cdp.cone_theta_x))
        print("%-20s %20.10f" % ("cone_theta_y", cdp.cone_theta_y))
        if cdp.model == MODEL_PSEUDO_ELLIPSE:
            print("%-20s %20.10f" % ("cone_sigma_max", cdp.cone_sigma_max))
        print("%-20s %20.10f" % ("eigen_alpha", cdp.eigen_alpha))
        print("%-20s %20.10f" % ("eigen_beta", cdp.eigen_beta))
        print("%-20s %20.10f" % ("eigen_gamma", cdp.eigen_gamma))
        print("%-20s\n%s" % ("eigenframe", axes_new))


def pivot(pivot=None, order=1, fix=False):
    """Set the pivot point for the 2 body motion.

    @keyword pivot: The pivot point of the two bodies (domains, etc.) in the structural coordinate system.
    @type pivot:    list of num
    @keyword order: The ordinal number of the pivot point.  The value of 1 is for the first pivot point, the value of 2 for the second pivot point, and so on.
    @type order:    int
    @keyword fix:   A flag specifying if the pivot point should be fixed during optimisation.
    @type fix:      bool
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Store the fixed flag.
    cdp.pivot_fixed = fix

    # No pivot given, so update the model if needed and quit.
    if pivot == None:
        if hasattr(cdp, 'model'):
            update_model()
        return

    # Convert the pivot to a numpy array.
    pivot = array(pivot, float64)

    # Check the pivot validity.
    is_float_array(pivot, name='pivot point', size=3)

    # Store the pivot point and fixed flag.
    if order == 1:
        cdp.pivot_x = pivot[0]
        cdp.pivot_y = pivot[1]
        cdp.pivot_z = pivot[2]
    else:
        # The variable names.
        name_x = 'pivot_x_%i' % order
        name_y = 'pivot_y_%i' % order
        name_z = 'pivot_z_%i' % order

        # Store the variables.
        setattr(cdp, name_x, pivot[0])
        setattr(cdp, name_y, pivot[1])
        setattr(cdp, name_z, pivot[2])

    # Update the model.
    if hasattr(cdp, 'model'):
        update_model()


def quad_int(flag=False):
    """Turn the high precision Scipy quadratic numerical integration on or off.

    @keyword flag:  The flag which if True will perform high precision numerical integration via the scipy.integrate quad(), dblquad() and tplquad() integration methods rather than the rough quasi-random numerical integration.
    @type flag:     bool
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Store the flag.
    cdp.quad_int = flag


def ref_domain(ref=None):
    """Set the reference domain for the frame order, multi-domain models.

    @param ref: The reference domain.
    @type ref:  str
    """

    # Checks.
    check_pipe()
    check_domain(domain=ref, escalate=0)

    # Set the reference domain.
    cdp.ref_domain = ref

    # Update the model.
    if hasattr(cdp, 'model'):
        update_model()


def select_model(model=None):
    """Select the Frame Order model.

    @param model:   The Frame Order model.  This can be one of 'pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor', 'iso cone', 'iso cone, torsionless', 'iso cone, free rotor', 'rotor', 'rigid', 'free rotor', 'double rotor'.
    @type model:    str
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Test if the model name exists.
    if not model in MODEL_LIST:
        raise RelaxError("The model name '%s' is invalid, it must be one of %s." % (model, MODEL_LIST))

    # Set the model
    cdp.model = model

    # Initialise the list of model parameters.
    cdp.params = []

    # Set the integration method if needed.
    if not hasattr(cdp, 'quad_int'):
        # Scipy quadratic numerical integration.
        if cdp.model in []:
            cdp.quad_int = True

        # Quasi-random numerical integration.
        else:
            cdp.quad_int = False

    # Update the model.
    update_model()


def simulate(file="simulation.pdb.bz2", dir=None, step_size=2.0, snapshot=10, total=1000, model=1, force=True):
    """Pseudo-Brownian dynamics simulation of the frame order motions.

    @keyword file:      The PDB file for storing the frame order pseudo-Brownian dynamics simulation.  The compression is determined automatically by the file extensions '*.pdb', '*.pdb.gz', and '*.pdb.bz2'.
    @type file:         str
    @keyword dir:       The directory name to place the file into.
    @type dir:          str or None
    @keyword step_size: The rotation will be of a random direction but with this fixed angle.  The value is in degrees.
    @type step_size:    float
    @keyword snapshot:  The number of steps in the simulation when snapshots will be taken.
    @type snapshot:     int
    @keyword total:     The total number of snapshots to take before stopping the simulation.
    @type total:        int
    @keyword model:     Only one model from an analysed ensemble of structures can be used for the pseudo-Brownian simulation, as the simulation and corresponding PDB file consists of one model per simulation.
    @type model:        int
    @keyword force:     A flag which, if set to True, will overwrite the any pre-existing file.
    @type force:        bool
    """

    # Printout.
    print("Pseudo-Brownian dynamics simulation of the frame order motions.")

    # Checks.
    pipes.test()
    check_model()
    check_domain()
    check_parameters()
    check_pivot()

    # Skip the rigid model.
    if cdp.model == MODEL_RIGID:
        print("Skipping the rigid model.")
        return

    # Open the output file.
    file = open_write_file(file_name=file, dir=dir, force=force)

    # The parameter values.
    values = assemble_param_vector()
    params = {}
    i = 0
    for name in cdp.params:
        params[name] = values[i]
        i += 1

    # The structure.
    structure = deepcopy(cdp.structure)
    if structure.num_models() > 1:
        structure.collapse_ensemble(model_num=model)

    # The pivot points.
    num_states = 1
    if cdp.model == MODEL_DOUBLE_ROTOR:
        num_states = 2
    pivot = zeros((num_states, 3), float64)
    for i in range(num_states):
        pivot[i] = generate_pivot(order=i+1, pdb_limit=True)

    # Shift to the average position.
    average_position(structure=structure, models=[None])

    # The motional eigenframe.
    frame = generate_axis_system()

    # Create the distribution.
    brownian(file=file, model=cdp.model, structure=structure, parameters=params, eigenframe=frame, pivot=pivot, atom_id=domain_moving(), step_size=step_size, snapshot=snapshot, total=total)

    # Close the file.
    file.close()


def sobol_setup(max_num=200, oversample=100):
    """Oversampling setup for the quasi-random Sobol' sequence used for numerical PCS integration.

    @keyword max_num:       The maximum number of integration points N.
    @type max_num:          int
    @keyword oversample:    The oversampling factor Ov used for the N * Ov * 10**M, where M is the number of dimensions or torsion-tilt angles for the system.
    @type oversample:       int
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Throw a warning to the user if not enough points are being used.
    if max_num < 200:
        warn(RelaxWarning("To obtain reliable results in a frame order analysis, the maximum number of integration points should be greater than 200."))
 
    # Store the values.
    cdp.sobol_max_points = max_num
    cdp.sobol_oversample = oversample

    # Count the number of Sobol' points for the current model.
    count_sobol_points()
