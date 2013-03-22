###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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

# Module docsting.
"""Module containing the functions which interface relax with OpenDX."""


# Python module imports.
from os import system

# relax module imports.
from opendx import isosurface_3D
from lib.errors import RelaxError
from relax_io import test_binary


def map(params=None, map_type='Iso3D', spin_id=None, inc=20, lower=None, upper=None, axis_incs=10, file_prefix="map", dir="dx", point=None, point_file="point", remap=None):
    """Map the space corresponding to the spin identifier and create the OpenDX files.

    @keyword params:        
    @type params:           
    @keyword map_type:      The type of map to create.  The available options are:
                                - 'Iso3D', a 3D isosurface visualisation of the space.
    @type map_type:         str
    @keyword spin_id:       The spin identification string.
    @type spin_id:          str
    @keyword inc:           The resolution of the plot.  This is the number of increments per
                            dimension.
    @type inc:              int
    @keyword lower:         The lower bounds of the space to map.  If supplied, this should be a
                            list of floats, its length equal to the number of parameters in the
                            model.
    @type lower:            None or list of float
    @keyword upper:         The upper bounds of the space to map.  If supplied, this should be a
                            list of floats, its length equal to the number of parameters in the
                            model.
    @type upper:            None or list of float
    @keyword axis_incs:     The number of tick marks to display in the OpenDX plot in each
                            dimension.
    @type axis_incs:        int
    @keyword file_prefix:   The file prefix for all the created files.
    @type file_prefix:      str
    @keyword dir:           The directory to place the files into.
    @type dir:              str or None
    @keyword point:         If supplied, a red sphere will be placed at these coordinates.
    @type point:            None or list of float
    @keyword point_file:    The file prefix for the point output files.
    @type point_file:       str or None
    @keyword remap:         A function which is used to remap the space.  The function should accept
                            the parameter array (list of float) and return an array of equal length
                            (again list of float).
    @type remap:            None or func
    """

    # Check the args.
    if inc <= 1:
        raise RelaxError("The increment value needs to be greater than 1.")
    if axis_incs <= 1:
        raise RelaxError("The axis increment value needs to be greater than 1.")

    # Space type.
    if map_type.lower() == "iso3d":
        if len(params) != 3:
            raise RelaxError("The 3D isosurface map requires a 3 parameter model.")

        # Create the map.
        isosurface_3D.Iso3D(params, spin_id, inc, lower, upper, axis_incs, file_prefix, dir, point, point_file, remap)
    else:
        raise RelaxError("The map type '" + map_type + "' is not supported.")


def run(file_prefix="map", dir="dx", dx_exe="dx", vp_exec=True):
    """Execute OpenDX.

    @keyword file_prefix:   The file prefix for all the created files.
    @type file_prefix:      str
    @keyword dir:           The directory to place the files into.
    @type dir:              str or None
    @keyword dx_exe:        The path to the OpenDX executable file.  This can be changed if the
                            binary 'dx' is not located in the system path.
    @type dx_exe:           str
    @keyword vp_exec:       If True, then the OpenDX visual program will be launched.
    @type vp_exec:          bool
    """

    # Text for changing to the directory dir.
    dir_text = ""
    if dir != None:
        dir_text = " -directory " + dir

    # Text for executing OpenDX.
    execute_text = ""
    if vp_exec:
        execute_text = " -execute"

    # Test the binary file string corresponds to a valid executable.
    test_binary(dx_exe)

    # Run OpenDX.
    system(dx_exe + dir_text + " -program " + file_prefix + ".net" + execute_text + " &")
