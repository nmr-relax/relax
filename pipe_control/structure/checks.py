###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
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

# relax module imports.
from lib.checks import Check
from lib.errors import RelaxError
from pipe_control.pipes import cdp_name, get_pipe


def check_structure_func(pipe_name=None):
    """Test if structural data is present.

    @return:        The initialised RelaxError object or nothing.
    @rtype:         None or RelaxError instance
    """

    # Defaults.
    if pipe_name == None:
        pipe_name = cdp_name()

    # Get the data pipe.
    dp = get_pipe(pipe_name)

    # Test if the structure exists.
    if not hasattr(dp, 'structure'):
        return RelaxError("No structural data is present in the current data pipe.")

    # Check for models:
    if not dp.structure.num_models():
        return RelaxError("The structural object in the current data pipe contains no models.")

    # Check for molecules.
    if not dp.structure.num_molecules():
        return RelaxError("The structural object in the current data pipe contains no molecules.")

# Create the checking object.
check_structure = Check(check_structure_func)
