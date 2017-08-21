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

# Python module imports.
from re import search
import sys

# Add the path to the relax base directory.
sys.path.append(sys.path[0])
sys.path[0] = '../..'

# relax module imports.
from prompt.interpreter import Interpreter


class Dummy_class:
    def __init__(self):
        # Some dummy data structures.
        self.script_file = None
        self.intro_string = ''
        self.dummy_mode = 1

        # Start the interpreter!
        self.interpreter = Interpreter(self)
        self.interpreter.run()

        # Get the names of the data structures.
        names = sorted(self.local.keys())

        # Alphabetically sort the names of the data structures.

        # Alphabetically sort the names of the data structures.
        for name in names:
            # Skip the name if it is in the blacklist.
            blacklist = ['Numeric', 'Scientific', 'intro_off', 'intro_on', 'pi', 'script']
            if name in blacklist:
                continue

            # Get the object.
            object = self.local[name]

            # Determine if the structure is user function containing class.
            if hasattr(object, '__relax_help__'):
                # Get the names of the data structures.
                names2 = sorted(dir(object))

                # Alphabetically sort the names of the data structures.
                for name2 in names2:
                    # Skip names begining with an underscore.
                    if search('^_', name2):
                        continue

                    # Get the object.
                    object2 = getattr(object, name2)

                    # Skip the object if there is no docstring.
                    if not hasattr(object2, '__doc__') or not object2.__doc__:
                        continue

                    # Printout.
                    print(name + '.' + name2)

                # Done.
                continue

            # Skip the object if there is no docstring.
            if not hasattr(object, '__doc__') or not object.__doc__:
                continue

            # Print the name.
            print(name)

# Exec.
Dummy_class()
