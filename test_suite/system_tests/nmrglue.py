##############################################################################
#                                                                             #
# Copyright (C) 2011-2014 Edward d'Auvergne                                   #
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
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase
from extern import nmrglue


class Nmrglue(SystemTestCase):
    """TestCase class for the functionality of the external module nmrglue.
    This is from U{Task #7873<https://gna.org/task/index.php?7873>}: Write wrapper function to nmrglue, to read .ft2 files and process them."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create a data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def test_version(self):
        """Test version of nmrglue."""

        # Test version.
        ng_vers = nmrglue.__version__
        print("Version of nmrglue is %s"%ng_vers)

        # Assert the version to be 0.4.
        self.assertEqual(ng_vers, '0.4')
