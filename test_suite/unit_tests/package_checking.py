###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
from os import listdir
from re import search
from unittest import TestCase


class PackageTestCase(TestCase):
    """Base class for the unit tests of the relax packages."""

    def test___all__(self):
        """Check if all modules are located within the __all__ list."""

        print("The %s.__all__ list: %s" % (self.package_name, self.package.__all__))

        # Loop over all modules.
        files = listdir(self.package_path)
        for file in files:
            # Only look at the '*.py' files.
            if not search('.py$', file):
                continue

            # Skip the __init__.py file.
            if file == '__init__.py':
                continue

            # Remove the '.py' part.
            module = file[:-3]

            # Print out.
            print("\nFile:   %s" % file)
            print("Module: %s" % module)

            # Check if the module is in __all__.
            self.assert_(module in self.package.__all__)
