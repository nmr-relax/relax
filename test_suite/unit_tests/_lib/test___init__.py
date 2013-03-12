###############################################################################
#                                                                             #
# Copyright (C) 2009-2013 Edward d'Auvergne                                   #
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
import sys

# relax module imports.
from test_suite.unit_tests.package_checking import PackageTestCase
import lib


class Test___init__(PackageTestCase):
    """Unit tests for the lib package."""

    def setUp(self):
        """Set up for the package checking."""

        self.package = lib
        self.package_name = 'lib'
        self.package_path = sys.path[0] + sep + 'lib'

        # Mac OS X application fix:  Handle the py2app extension placing the Python directories into Resources/lib/python2.7 (Resources/lib is the relax lib package).
        self.blacklist = ['python2.7']
