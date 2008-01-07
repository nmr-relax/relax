###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Python module imports.
from math import sqrt
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store


class N_state_model(TestCase):
    """Class for testing various aspects specific to the N-state model."""

    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()



    def test_5_state_xz(self):
        """A 5-state model in the xz-plane (no pivotting of alpha).

        The 5 states correspond to the Euler angles (z-y-z notation):
            State 1:    {0, pi/4, 0}
            State 2:    {0, pi/8, 0}
            State 3:    {0, 0, 0}
            State 4:    {0, -pi/8, 0}
            State 5:    {0, -pi/4, 0}
        """

        # Place the script file name into self.relax.script_file.
        self.relax.script_file = 'test_suite/system_tests/scripts/5_state_xz.py'

        # Execute relax in script mode.
        self.relax.interpreter.run()
