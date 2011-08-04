###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""The value user function GUI elements."""

# Python module imports.
import wx

# GUI module imports.
from base import UF_base, UF_page
from gui.misc import gui_to_str, str_to_gui
from gui.paths import WIZARD_IMAGE_PATH
from gui.wizard import Wiz_window


# The container class.
class Grace(UF_base):
    """The container class for holding all GUI elements."""

    def view(self, event, file=None):
        """The grace.view user function.

        @param event:   The wx event.
        @type event:    wx event
        @keyword file:  The file to start the user function with.
        @type file:     str
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=900, size_y=500, title=self.get_title('grace', 'view'))
        page = View_page(wizard, self.gui)
        wizard.add_page(page)

        # Default file name.
        if file:
            page.file.SetValue(file)

        # Execute the wizard.
        wizard.run()



class View_page(UF_page):
    """The grace.view() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'grace.png'
    uf_path = ['grace', 'view']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The Grace file:", message="Grace file selection", wildcard="Grace files (*.agr)|*.agr", style=wx.FD_OPEN, tooltip=self.uf._doc_args_dict['file'])

        # The Grace exec file.
        self.grace_exe = self.file_selection(sizer, "The Grace executable:", message="Grace executable file selection", style=wx.FD_OPEN, tooltip=self.uf._doc_args_dict['grace_exe'])
        self.grace_exe.SetValue(str_to_gui('xmgrace'))


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetValue())

        # The executable.
        grace_exe = gui_to_str(self.grace_exe.GetValue())

        # Open the file.
        self.gui.interpreter.grace.view(file=file, grace_exe=grace_exe)
