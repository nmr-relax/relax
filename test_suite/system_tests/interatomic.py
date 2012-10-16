###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""System tests of the interatomic data container operations."""


# Python module imports.
from os import sep

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Interatomic(SystemTestCase):
    """Class for testing the interatomic functions."""

    def test_manipulation(self):
        """Test the manipulation of interatomic data containers."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'interatomic_tests.py')

        # The data.
        select = [True, False] + [True]*3 + [False]*2 + [True]*5 + [False]*2 + [True, False]

        # Check the data.
        self.assertEqual(len(cdp.interatomic), 16)
        for i in range(len(cdp.interatomic)):
            # A printout to know where the problem is.
            print("Checking container:  %-30s %-30s" % (cdp.interatomic[i].spin_id1, cdp.interatomic[i].spin_id2))

            # The container checks.
            self.assertEqual(cdp.interatomic[i].select, select[i])
