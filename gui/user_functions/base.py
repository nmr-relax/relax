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

# Module docstring.
"""Base class module for the user function GUI elements."""

# relax GUI imports.
from gui.wizard import Wiz_panel


class UF_base:
    """User function GUI element base class."""

    def __init__(self, gui, interpreter):
        """Set up the user function class."""

        # Store the args.
        self.gui = gui
        self.interpreter = interpreter

        # Specific set up.
        self.setup()


    def setup(self):
        """Dummy method to be overwritten."""


class UF_panel(Wiz_panel):
    """User function specific panel for the wizards."""

    def __init__(self, parent, gui, interpreter):
        """Set up the window.

        @param parent:      The parent class containing the GUI and interpreter objects.
        @type parent:       class instance
        @param gui:         The GUI base object.
        @type gui:          wx.Frame instance
        @param interpreter: The relax interpreter.
        @type interpreter:  prompt.interpreter.Interpreter instance
        """

        # Store the args.
        self.gui = gui
        self.interpreter = interpreter

        # Execute the base class method.
        super(UF_panel, self).__init__(parent)
