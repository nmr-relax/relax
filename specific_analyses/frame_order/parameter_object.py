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
"""The module for the frame order parameter list object."""

# Python module imports.
from math import pi

# relax module imports.
from lib.errors import RelaxError
from specific_analyses.parameter_object import Param_list


def angle_upper_excluding_bound(incs=None, model_info=None):
    """Determine the upper grid bound for the angular parameters, excluding the bound value.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The model information from model_loop().  This is unused.
    @type model_info:       None
    @return:                The upper grid search bound for the angular parameters, excluding the bound value.
    @rtype:                 float
    """

    # Handle inc values of None or 1.
    if incs in [None, 1]:
        return 2.0 * pi

    # Return the upper limit which is one inc before 2pi.
    return 2.0*pi * (1.0 - 1.0/(incs+1))


def axis_alpha_upper(incs=None, model_info=None):
    """Determine the upper grid bound for the axis alpha angle.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The model information from model_loop().  This is unused.
    @type model_info:       None
    @return:                The upper grid search bound for the axis alpha angle.
    @rtype:                 float
    """

    # Handle inc values of None or 1.
    if incs in [None, 1]:
        return pi

    # Return the upper limit which is one inc before pi.
    return pi * (1.0 - 1.0/(incs+1))


def cone_angle_lower(incs=None, model_info=None):
    """Determine the lower grid bound for the cone and torsion angles.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The model information from model_loop().  This is unused.
    @type model_info:       None
    @return:                The lower grid search bound for the cone and torsion angles.
    @rtype:                 float
    """

    # Handle inc values of None or 1.
    if incs in [None, 1]:
        return 0.0

    # Return the lower limit, excluding the first point.
    return pi * (1.0/(incs+2))


def cone_angle_upper(incs=None, model_info=None):
    """Determine the upper grid bound for the cone and torsion angles.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The model information from model_loop().  This is unused.
    @type model_info:       None
    @return:                The upper grid search bound for the cone and torsion angles.
    @rtype:                 float
    """

    # Handle inc values of None or 1.
    if incs in [None, 1]:
        return pi

    # Return the upper limit, excluding the last point.
    return pi * (1.0 - 1.0/(incs+2))


def pivot_grid_bound(param=None, extent=10.0):
    """Determine the grid bounds for the pivot coordinates.

    @keyword param:     The parameter to find the bound for.  This should be one of 'pivot_x', 'pivot_y', or 'pivot_z'.
    @type param:        str
    @keyword extent:    The length in Angstrom to extend out from the current coordinate to reach the grid bound.
    @type extent:       float
    @return:            The grid search bound for the given coordinate.
    @rtype:             float
    """

    # No pivot set.
    if not hasattr(cdp, param):
        raise RelaxError("The pivot point has not been set, cannot determine the grid search bounds.")

    # The value.
    val = getattr(cdp, param)

    # Return the bound.
    return val + extent


def pivot_x_lower(incs=None, model_info=None, size=10.0):
    """Determine the lower grid bound for the pivot X coordinate.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The model information from model_loop().  This is unused.
    @type model_info:       None
    @keyword size:          The half grid size in Angstrom.
    @type size:             float
    @return:                The lower grid search bound for the coordinate.
    @rtype:                 float
    """

    # Return the value.
    return pivot_grid_bound(param='pivot_x', extent=-size)


def pivot_x_upper(incs=None, model_info=None, size=10.0):
    """Determine the upper grid bound for the pivot X coordinate.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The model information from model_loop().  This is unused.
    @type model_info:       None
    @keyword size:          The half grid size in Angstrom.
    @type size:             float
    @return:                The upper grid search bound for the coordinate.
    @rtype:                 float
    """

    # Return the value.
    return pivot_grid_bound(param='pivot_x', extent=size)


def pivot_y_lower(incs=None, model_info=None, size=10.0):
    """Determine the lower grid bound for the pivot Y coordinate.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The model information from model_loop().  This is unused.
    @type model_info:       None
    @keyword size:          The half grid size in Angstrom.
    @type size:             float
    @return:                The lower grid search bound for the coordinate.
    @rtype:                 float
    """

    # Return the value.
    return pivot_grid_bound(param='pivot_y', extent=-size)


def pivot_y_upper(incs=None, model_info=None, size=10.0):
    """Determine the upper grid bound for the pivot Y coordinate.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The model information from model_loop().  This is unused.
    @type model_info:       None
    @keyword size:          The half grid size in Angstrom.
    @type size:             float
    @return:                The upper grid search bound for the coordinate.
    @rtype:                 float
    """

    # Return the value.
    return pivot_grid_bound(param='pivot_y', extent=size)


def pivot_z_lower(incs=None, model_info=None, size=10.0):
    """Determine the lower grid bound for the pivot Z coordinate.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The model information from model_loop().  This is unused.
    @type model_info:       None
    @keyword size:          The half grid size in Angstrom.
    @type size:             float
    @return:                The lower grid search bound for the coordinate.
    @rtype:                 float
    """

    # Return the value.
    return pivot_grid_bound(param='pivot_z', extent=-size)


def pivot_z_upper(incs=None, model_info=None, size=10.0):
    """Determine the upper grid bound for the pivot Z coordinate.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The model information from model_loop().  This is unused.
    @type model_info:       None
    @keyword size:          The half grid size in Angstrom.
    @type size:             float
    @return:                The upper grid search bound for the coordinate.
    @rtype:                 float
    """

    # Return the value.
    return pivot_grid_bound(param='pivot_z', extent=size)



class Frame_order_params(Param_list):
    """The frame order parameter list singleton."""

    # Class variable for storing the class instance (for the singleton design pattern).
    _instance = None

    def __init__(self):
        """Define all the parameters of the analysis."""

        # The object is already initialised.
        if self._initialised: return

        # Execute the base class __init__ method.
        Param_list.__init__(self)

        # Add the model variables.
        self._add_model_info()

        # Add the base data.
        self._add_align_data()

        # Add the parameters of all models.
        self._add(
            'pivot_x',
            scope = 'global',
            units = 'Angstrom',
            desc = 'The pivot point position x coordinate',
            py_type = float,
            set = 'params',
            scaling = 1e2,
            grid_lower = pivot_x_lower,
            grid_upper = pivot_x_upper,
            err = True,
            sim = True
        )
        self._add(
            'pivot_y',
            scope = 'global',
            units = 'Angstrom',
            desc = 'The pivot point position y coordinate',
            py_type = float,
            set = 'params',
            scaling = 1e2,
            grid_lower = pivot_y_lower,
            grid_upper = pivot_y_upper,
            err = True,
            sim = True
        )
        self._add(
            'pivot_z',
            scope = 'global',
            units = 'Angstrom',
            desc = 'The pivot point position z coordinate',
            py_type = float,
            set = 'params',
            scaling = 1e2,
            grid_lower = pivot_z_lower,
            grid_upper = pivot_z_upper,
            err = True,
            sim = True
        )
        self._add(
            'ave_pos_x',
            scope = 'global',
            units = 'Angstrom',
            desc = 'The average position x translation',
            py_type = float,
            set = 'params',
            grid_lower = -5,
            grid_upper = 5,
            err = True,
            sim = True
        )
        self._add(
            'ave_pos_y',
            scope = 'global',
            units = 'Angstrom',
            desc = 'The average position y translation',
            py_type = float,
            set = 'params',
            grid_lower = -5,
            grid_upper = 5,
            err = True,
            sim = True
        )
        self._add(
            'ave_pos_z',
            scope = 'global',
            units = 'Angstrom',
            desc = 'The average position z translation',
            py_type = float,
            set = 'params',
            grid_lower = -5,
            grid_upper = 5,
            err = True,
            sim = True
        )
        self._add(
            'ave_pos_alpha',
            scope = 'global',
            units = 'rad',
            desc = 'The average position alpha Euler angle',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = angle_upper_excluding_bound,
            err = True,
            sim = True
        )
        self._add(
            'ave_pos_beta',
            scope = 'global',
            units = 'rad',
            desc = 'The average position beta Euler angle',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = pi,
            err = True,
            sim = True
        )
        self._add(
            'ave_pos_gamma',
            scope = 'global',
            units = 'rad',
            desc = 'The average position gamma Euler angle',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = angle_upper_excluding_bound,
            err = True,
            sim = True
        )
        self._add(
            'eigen_alpha',
            scope = 'global',
            units = 'rad',
            desc = 'The Eigenframe alpha Euler angle',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = angle_upper_excluding_bound,
            err = True,
            sim = True
        )
        self._add(
            'eigen_beta',
            scope = 'global',
            units = 'rad',
            desc = 'The Eigenframe beta Euler angle',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = pi,
            err = True,
            sim = True
        )
        self._add(
            'eigen_gamma',
            scope = 'global',
            units = 'rad',
            desc = 'The Eigenframe gamma Euler angle',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = angle_upper_excluding_bound,
            err = True,
            sim = True
        )
        self._add(
            'axis_theta',
            scope = 'global',
            units = 'rad',
            desc = 'The cone axis polar angle (for the isotropic cone model)',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = pi,
            err = True,
            sim = True
        )
        self._add(
            'axis_phi',
            scope = 'global',
            units = 'rad',
            desc = 'The cone axis azimuthal angle (for the isotropic cone model)',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = angle_upper_excluding_bound,
            err = True,
            sim = True
        )
        self._add(
            'axis_alpha',
            scope = 'global',
            units = 'rad',
            desc = 'The rotor axis alpha angle (the rotation angle out of the xy plane)',
            py_type = float,
            set = 'params',
            grid_lower = -pi,
            grid_upper = axis_alpha_upper,
            err = True,
            sim = True
        )
        self._add(
            'cone_theta_x',
            scope = 'global',
            units = 'rad',
            desc = 'The pseudo-ellipse cone opening half-angle for the x-axis',
            py_type = float,
            set = 'params',
            grid_lower = cone_angle_lower,
            grid_upper = cone_angle_upper,
            err = True,
            sim = True
        )
        self._add(
            'cone_theta_y',
            scope = 'global',
            units = 'rad',
            desc = 'The pseudo-ellipse cone opening half-angle for the y-axis',
            py_type = float,
            set = 'params',
            grid_lower = cone_angle_lower,
            grid_upper = cone_angle_upper,
            err = True,
            sim = True
        )
        self._add(
            'cone_theta',
            scope = 'global',
            units = 'rad',
            desc = 'The isotropic cone opening half-angle',
            py_type = float,
            set = 'params',
            grid_lower = cone_angle_lower,
            grid_upper = cone_angle_upper,
            err = True,
            sim = True
        )
        self._add(
            'cone_s1',
            scope = 'global',
            units = '',
            desc = 'The isotropic cone order parameter',
            py_type = float,
            set = 'params',
            grid_lower = -0.125,
            grid_upper = 1.0,
            err = True,
            sim = True
        )
        self._add(
            'cone_sigma_max',
            scope = 'global',
            units = 'rad',
            desc = 'The torsion angle',
            py_type = float,
            set = 'params',
            grid_lower = cone_angle_lower,
            grid_upper = cone_angle_upper,
            err = True,
            sim = True
        )

        # Add minimisation structures.
        self._add_min_data(min_stats_global=True)

        # Set up the user function documentation.
        self._set_uf_title("Frame order parameters")
        self._uf_param_table(label="table: frame order parameters", caption="Frame order parameters.", scope='global')
        self._uf_param_table(label="table: frame order parameter value setting with defaults", caption="Frame order parameter value setting.", scope='global', default=True)
