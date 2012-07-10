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

# Module docstring.
"""GUI tests for the BMRB related activities."""

# relax module imports.
import dep_check
from test_suite.gui_tests.base_classes import GuiTestCase
from test_suite import system_tests


class Bmrb(GuiTestCase, system_tests.bmrb.Bmrb):
    """Class for testing the BMRB related functions in the GUI."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Force execution of the GuiTestCase __init__ method.
        GuiTestCase.__init__(self, methodName)
