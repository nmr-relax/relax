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
"""The script user functions."""

# Python module imports.
import thread
import wx

# relax module imports.
from status import Status; status = Status()

# GUI module imports.
from base import UF_base
from gui.filedialog import RelaxFileDialog


class Script(UF_base):
    """The script user function GUI class."""

    def run(self, event, file=None):
        """The script user function GUI element.

        @param event:   The wx event.
        @type event:    wx event
        @param file:    The path of the script to execute, if already known.  If not given, a file selection dialog will appear.
        @type file:     str
        """

        # User selection of the file.
        if not file:
            dialog = RelaxFileDialog(parent=None, message='Select the relax script to execute', wildcard='relax scripts (*.py)|*.py', style=wx.FD_OPEN)

            # Show the dialog and catch if no file has been selected.
            if status.show_gui and dialog.ShowModal() != wx.ID_OK:
                # Don't do anything.
                return

            # The file.
            file = dialog.get_file()

        # Show the relax controller.
        if status.show_gui:
            app = wx.GetApp()
            app.gui.controller.Show()

        # Execute the script in a thread.
        id = thread.start_new_thread(self.script_exec, (file,))


    def script_exec(self, file):
        """Execute the script in a thread.

        @param file:    The script file name.
        @type file:     str
        """

        # Execute the user function.
        self.gui.interpreter.queue('script', str(file))
