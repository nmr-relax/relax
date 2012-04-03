###############################################################################
#                                                                             #
# Copyright (C) 2009-2012 Edward d'Auvergne                                   #
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
from os import sep
import sys

# relax module imports.
from test_suite.unit_tests.package_checking import PackageTestCase
import multi


class Test___init__(PackageTestCase):
    """Unit tests for the multi package."""

    def setUp(self):
        """Set up for the package checking."""

        self.package = multi
        self.package_name = 'multi'
        self.package_path = sys.path[0] + sep + 'multi'

        # Blacklisted scripts.
        self.blacklist = ['test_implementation.py', 'test_implementation2.py']
