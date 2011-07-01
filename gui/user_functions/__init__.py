###############################################################################
#                                                                             #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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
from relax_errors import RelaxError

# GUI module imports.
from molecule import Molecule
from pipes import Pipes
from residue import Residue
from relax_data import Relax_data
from script import Script
from sequence import Sequence
from spin import Spin
from structure import Structure
from value import Value


# The package __all__ list.
__all__ = ['base',
           'molecule',
           'pipes',
           'residue',
           'relax_data',
           'script',
           'sequence',
           'spin',
           'structure',
           'value']


class User_functions:
    """Container for all the user function GUI elements.

    This uses the observer design pattern to allow for GUI updates upon completion of a user function.
    """

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
        self.pipes = Pipes(self.gui, self.interpreter)
        self.residue = Residue(self.gui, self.interpreter)
        self.relax_data = Relax_data(self.gui, self.interpreter)
        self.script = Script(self.gui, self.interpreter)
        self.sequence = Sequence(self.gui, self.interpreter)
        self.spin = Spin(self.gui, self.interpreter)
        self.structure = Structure(self.gui, self.interpreter)
        self.value = Value(self.gui, self.interpreter)

        # The dictionary of callback methods.
        self._callback = {}


    def destroy(self):
        """Close all windows."""

        # Send the commands onwards to the user function classes.
        self.molecule.destroy()
        self.pipes.destroy()
        self.residue.destroy()
        self.relax_data.destroy()
        self.sequence.destroy()
        self.spin.destroy()
        self.structure.destroy()
        self.value.destroy()


    def notify_observers(self):
        """Notify all observers that a user function has completed."""

        # Loop over the callback methods and execute them.
        for key in self._callback.keys():
            self._callback[key]()


    def register_observer(self, key, method):
        """Register a method to be called when all user functions complete.

        @param key:     The key to identify the observer's method.
        @type key:      str
        @param method:  The observer's method to be called after completion of the user function.
        @type method:   method
        """

        # Already exists.
        if key in self._callback.keys():
            raise RelaxError("The key '%s' already exists." % key)

        # Add the method to the dictionary of callbacks.
        self._callback[key] = method


    def unregister_observer(self, key):
        """Unregister the method corresponding to the key.

        @param method:  The observer's method to be called after completion of the user function.
        @type method:   method
        """

        # Does not exist.
        if key not in self._callback.keys():
            raise RelaxError("The key '%s' does not exist." % key)

        # Remove the method from the dictionary of callbacks.
        self._callback.pop(key)
