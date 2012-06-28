###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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

# Module docstring.
"""System tests of the interatomic data container operations."""


# Python module imports.
from os import sep

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


class Interatomic(SystemTestCase):
    """Class for testing the interatomic functions."""

    def test_manipulation(self):
        """Test the manipulation of interatomic data containers."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'interatomic_tests.py')

        # The data.
        select = [True]*5 + [False]*2 + [True]*5 + [False]*2

        # Check the data.
        self.assertEqual(len(cdp.interatomic), 14)
        for i in range(len(cdp.interatomic)):
            # A print out to know where the problem is.
            print("Checking container:  %-30s %-30s" % (cdp.interatomic[i].spin_id1, cdp.interatomic[i].spin_id2))

            # The container checks.
            self.assertEqual(cdp.interatomic[i].select, select[i])
