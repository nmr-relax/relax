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
from os import listdir, sep
from re import search
import sys
from unittest import TestCase

# relax module imports.
from generic_fns import structure


class Test___init__(TestCase):
    """Unit tests for the generic_fns.structure package."""

    def test___all__(self):
        """Check if the generic_fns.structure modules are located within the __all__ list."""

        # Path to the files.
        path = sys.path[0] + sep + 'generic_fns' + sep + 'structure'

        print("The generic_fns.structure.__all__ list: %s" % structure.__all__)

        # Loop over all modules.
        files = listdir(path)
        for file in files:
            # Only look at the '*.py' files.
            if not search('.py$', file):
                continue

            # Skip __init__.py
            if file == '__init__.py':
                continue

            # Remove the '.py' part.
            module = file[:-3]

            # Print out.
            print("\nFile:   %s" % file)
            print("Module: %s" % module)

            # Check if the module is in __all__.
            self.assert_(module in structure.__all__)
