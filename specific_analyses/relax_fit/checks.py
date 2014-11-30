###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
"""Module of functions for checking different aspects of the relaxation curve-fitting setup."""

# relax module imports.
from lib.checks import Check
from lib.errors import RelaxError
from pipe_control.mol_res_spin import spin_loop


def check_model_setup_func():
    """Check that the model has been correctly set up.

    @return:        The initialised RelaxError object or nothing.
    @rtype:         None or RelaxError instance
    """

    # Test if the model has been set.
    for spin in spin_loop():
        # Skip deselected spins.
        if not spin.select:
            continue

        # No model set.
        if not hasattr(spin, 'model'):
            return RelaxError("The exponential curve model has not been set, please use the relax_fit.select_model user function.")

# Create the checking object.
check_model_setup = Check(check_model_setup_func)
