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
from os import F_OK, access, listdir, sep
from re import search

# relax module imports.
from test_suite.unit_tests.base_classes import UnitTestCase


class PackageTestCase(UnitTestCase):
    """Base class for the unit tests of the relax packages."""

    def test___all__(self):
        """Check if all modules are located within the __all__ list."""

        # Initial printout.
        print("The %s.__all__ list: %s" % (self.package_name, self.package.__all__))

        # Check for modules/packages missing from the __all__ list.
        print("\nChecking for modules/packages missing from the __all__ list.")
        files = listdir(self.package_path)
        skip = ['__init__.py']
        for file in files:
            # Files and directories to skip.
            if file in skip:
                continue

            # Skip hidden files and directories.
            if search("^\.", file):
                continue

            # Skip blacklisted files.
            if hasattr(self, 'blacklist') and file in self.blacklist:
                continue

            # Remove the extension if needed.
            module = file
            if search('.py$', module):
                module = module[:-3]
            if search('.so$', module):
                module = module[:-3]

            # Printout.
            print("    Module/package:  %s" % module)

            # Check if the module is in __all__.
            self.assert_(module in self.package.__all__)

        # Check for modules/packages in the __all__ list which do not exist.
        print("\nChecking for modules/packages in the __all__ list which do not exist.")
        for module in self.package.__all__:
            # Printout.
            print("    Module/package: %s" % module)

            # Check for the module.
            if access(self.package_path+sep+module+'.py', F_OK):
                continue

            # Check for the package.
            if access(self.package_path+sep+module, F_OK):
                continue

            # Doesn't exist, so fail.
            self.fail()
