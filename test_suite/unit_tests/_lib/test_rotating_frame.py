###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""Unit tests of the lib.rotating_frame module."""

# Python module imports.
from os import sep

# relax module imports.
from lib.rotating_frame import calc_rotating_frame_params
from lib.errors import RelaxError
from pipe_control import state
from pipe_control.mol_res_spin import spin_loop
from test_suite.unit_tests.base_classes import UnitTestCase
from status import Status; status = Status()


class Test_rotating_frame(UnitTestCase):
    """Unit tests for the functions of the 'lib.rotating_frame' module."""

    def test_calc_rotating_frame_params(self):
        """Unit test of the calc_tilt_angle() function for R1rho setup.

        This uses the data of the saved state attached to U{bug #21344<https://gna.org/bugs/?21344>}.
        """

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21344_trunc.bz2'
        state.load_state(statefile, force=True)

        # Use calc_tilt_angle function
        calc_rotating_frame_params()

        # Test the existence of 
        for curspin, mol_name, res_num, res_name, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=False):
            print(curspin, mol_name, res_num, res_name, spin_id)
            self.assert_(hasattr(curspin, 'theta'))
