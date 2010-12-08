###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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

# Package docstring.
"""User function GUI elements."""

# relax module imports.
from prompt.interpreter import Interpreter

# GUI module imports.
from molecule import Molecule
from script import Script


# The package __all__ list.
__all__ = ['base',
           'molecule',
           'script']


class User_functions:
    """Container for all the user function GUI elements."""

    def __init__(self, gui):
        """Set up the container."""

        # Store the args.
        self.gui = gui

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=True, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # The user functions.
        self.molecule = Molecule(self.gui, self.interpreter)
        self.script = Script(self.gui, self.interpreter)


    def destroy(self):
        """Close all windows."""

        # Send the commands onwards to the user function classes.
        self.molecule.destroy()
