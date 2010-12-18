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

# Module docstring.
"""The script user functions."""

# Python module imports.
import thread

# GUI module imports.
from base import UF_base
from gui_bieri.filedialog import openfile


class Script(UF_base):
    """The script user function GUI class."""

    def run(self, event):
        """The script user function GUI element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # User selection of the file.
        file = openfile(msg='Select the relax script to execute')

        # Check the file.
        if not file:
            return

        # Show the relax controller.
        self.gui.controller.Show()

        # Execute the script in a thread.
        id = thread.start_new_thread(self.script_exec, (file,))


    def script_exec(self, file):
        """Execute the script in a thread.

        @param file:    The script file name.
        @type file:     str
        """

        # Execute the user function.
        self.interpreter.script(str(file))
