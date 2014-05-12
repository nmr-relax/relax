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
"""Verification tests for the status object."""

# Python module imports.
from unittest import TestCase

# relax module imports.
from status import Status; status = Status()


class Status_object(TestCase):
    """Test the relax status object."""

    def test_install_path(self):
        """Check that the relax installation path is set.

        This is to catch bug #22037 U{https://gna.org/bugs/index.php?22037}, the failure to load graphics in the GUI due to the relax installation path not being set up correctly.
        """

        # The installation path must be set.
        self.assertNotEqual(status.install_path, None)
        self.assertNotEqual(status.install_path, "")
