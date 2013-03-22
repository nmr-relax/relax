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
import target_functions


class Test___init__(PackageTestCase):
    """Unit tests for the target_functions package."""

    def setUp(self):
        """Set up for the package checking."""

        self.package = target_functions
        self.package_name = 'target_functions'
        self.package_path = sys.path[0] + sep + 'target_functions'
        self.blacklist = [
            'c_chi2.c',
            'c_chi2.h',
            'exponential.c',
            'exponential.h',
            'relax_fit.c',
            'relax_fit.h',
            'relax_fit.so'    # May not be present on all systems.
        ]
