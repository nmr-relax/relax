###############################################################################
#                                                                             #
# Copyright (C) 2008-2014 Edward d'Auvergne                                   #
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

# Python module imports.
from os import sep

# relax module imports.
from pipe_control import state
from specific_analyses.relax_disp.checks import get_times
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_checks(UnitTestCase):
    """Unit tests for the functions of the specific_analyses.relax_disp.checks module."""


    def test_get_times_cpmg(self):
        """Unit test of the get_times() function.

        This uses the data of the saved state attached to U{bug #21665<https://gna.org/bugs/?21665>}.
        """

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        state.load_state(statefile, force=True)

        # Check the return of get_times().
        times = get_times()
        for exp_type in times:
            print(times[exp_type])
            self.assertEqual(len(times[exp_type]), 2)






