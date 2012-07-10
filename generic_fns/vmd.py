###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2007-2009 Edward d'Auvergne                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for interfacing with VMD."""

# relax module imports.
import dep_check
from relax_errors import RelaxError, RelaxNoPdbError


def view():
    """Function for viewing the collection of molecules using VMD."""

    # Test if the module is available.
    if not dep_check.vmd_module:
        raise RelaxError("VMD is not available (cannot import Scientific.Visualization.VMD due to missing Numeric dependency).")

    # Test if the PDB file has been loaded.
    if not hasattr(cdp, 'structure'):
        raise RelaxNoPdbError

    # Create an empty scene.
    cdp.vmd_scene = VMD.Scene()

    # Add the molecules to the scene.
    for i in xrange(len(cdp.structure.structures)):
        cdp.vmd_scene.addObject(VMD.Molecules(cdp.structure.structures[i]))

    # View the scene.
    cdp.vmd_scene.view()
