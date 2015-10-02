###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
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
from numpy import array, dot, eye, float64, transpose, zeros
import sys
from warnings import warn

# relax module imports.
from lib.arg_check import is_float_array
from lib.errors import RelaxError
from lib.frame_order.rotor_axis import create_rotor_axis_alpha, create_rotor_axis_euler, create_rotor_axis_spherical
from lib.geometry.rotations import euler_to_R_zyz, two_vect_to_R
from lib.io import open_write_file
from lib.order import order_parameters
from lib.structure.cones import Iso_cone, Pseudo_elliptic
from lib.structure.geometric import generate_vector_residues
from lib.structure.internal.object import Internal
from lib.structure.represent.cone import cone
from lib.structure.represent.rotor import rotor_pdb
from lib.text.sectioning import subsection
from lib.warnings import RelaxWarning
from pipe_control import pipes
from pipe_control.structure.mass import pipe_centre_of_mass
from specific_analyses.frame_order.data import domain_moving
from specific_analyses.frame_order.geometric import create_ave_pos, create_distribution, create_geometric_rep
from specific_analyses.frame_order.parameters import update_model


def num_int_pts(num=200000):
    """Set the number of integration points to use in the quasi-random Sobol' sequence.

    @keyword num:   The number of integration points.
    @type num:      int
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Throw a warning to the user if not enough points are being used.
    if num < 1000:
        warn(RelaxWarning("To obtain reliable results in a frame order analysis, the number of integration points should be greater than 1000."))
 
    # Store the value.
    cdp.num_int_pts = num


def pdb_model(ave_pos_file="ave_pos.pdb", rep_file="frame_order.pdb", dist_file="domain_distribution.pdb", dir=None, size=30.0, inc=36, force=False, neg_cone=True):
    """Create 3 different PDB files for representing the frame order dynamics of the system.

    @keyword ave_pos_file:  The name of the file for the average molecule structure.
    @type ave_pos_file:     str or None
    @keyword rep_file:      The name of the file of the PDB representation of the frame order dynamics to create.
    @type rep_file:         str or None
    @keyword dist_file:     The name of the file which will contain multiple models spanning the full dynamics distribution of the frame order model.
    @type dist_file:        str or None
    @keyword dir:           The name of the directory to place the PDB file into.
    @type dir:              str
    @keyword size:          The size of the geometric object in Angstroms.
    @type size:             float
    @keyword inc:           The number of increments for the filling of the cone objects.
    @type inc:              int
    @keyword force:         Flag which if set to True will cause any pre-existing file to be overwritten.
    @type force:            bool
    @keyword neg_cone:      A flag which if True will cause the negative cone to be added to the representation.
    @type neg_cone:         bool
    """

    # Check that at least one PDB file name is given.
    if not ave_pos_file and not rep_file and not dist_file:
        raise RelaxError("Minimally one PDB file name must be supplied.")

    # Test if the current data pipe exists.
    check_pipe()

    # Create the average position structure.
    if ave_pos_file:
        create_ave_pos(file=ave_pos_file, dir=dir, force=force)

    # Nothing more to do for the rigid model.
    if cdp.model == 'rigid':
        return

    # Create the geometric representation.
    if rep_file:
        create_geometric_rep(file=rep_file, dir=dir, size=size, inc=inc, force=force, neg_cone=neg_cone)

    # Create the distribution.
    if dist_file:
        create_distribution(file=dist_file, dir=dir, force=force)


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


def ref_domain(ref=None):
    """Set the reference domain for the frame order, multi-domain models.

    @param ref: The reference domain.
    @type ref:  str
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Check that the domain is defined.
    if not hasattr(cdp, 'domain') or ref not in cdp.domain:
        raise RelaxError("The domain '%s' has not been defined.  Please use the domain user function." % ref)

    # Test if the reference domain exists.
    exists = False
    for tensor_cont in cdp.align_tensors:
        if hasattr(tensor_cont, 'domain') and tensor_cont.domain == ref:
            exists = True
    if not exists:
        raise RelaxError("The reference domain cannot be found within any of the loaded tensors.")

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
    if not model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor', 'iso cone', 'iso cone, torsionless', 'iso cone, free rotor', 'rotor', 'rigid', 'free rotor', 'double rotor']:
        raise RelaxError("The model name " + repr(model) + " is invalid.")

    # Set the model
    cdp.model = model

    # Initialise the list of model parameters.
    cdp.params = []

    # Update the model.
    update_model()
