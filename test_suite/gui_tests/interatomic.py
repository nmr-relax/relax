###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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

# relax module imports.
from test_suite.gui_tests.base_classes import GuiTestCase
from test_suite import system_tests


class Interatomic(GuiTestCase, system_tests.interatomic.Interatomic):
    """Class for testing various aspects specific to interatomic data containers."""


    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the base __init__ methods.
        super(Interatomic, self).__init__(methodName)


    def setUp(self):
        """Set up the tests by executing all base class setUp() methods."""

        # Call the base class methods.
        GuiTestCase.setUp(self)
        system_tests.interatomic.Interatomic.setUp(self)
