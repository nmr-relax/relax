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
"""The structure user function GUI elements."""

# Python module imports.
from os import sep
from string import split
from time import sleep
import wx

# relax module imports.
from generic_fns.pipes import cdp_name, pipe_names

# GUI module imports.
from base import UF_base, UF_page
from gui.misc import float_to_gui, gui_to_bool, gui_to_float, gui_to_int, gui_to_int_or_list, gui_to_str, gui_to_str_or_list, str_to_gui
from gui.paths import WIZARD_IMAGE_PATH


# The container class.
class Sys_info(UF_base):
    """The container class for holding all GUI elements."""

    def sys_info(self):
        """The sys_info user function."""

        # Create and execute the wizard.
        wizard = self.create_wizard(size_x=600, size_y=400, name='sys_info', uf_page=Sys_info_page, apply_button=False)
        wizard.run()



class Sys_info_page(UF_page):
    """The sys_info() user function page."""

    # Some class variables.
    uf_path = ['sys_info']

    def __init__(self, parent, sync=False):
        """Set up the window.

        @param parent:      The parent class containing the GUI.
        @type parent:       class instance
        @keyword sync:      A flag which is ignored.
        @type sync:         bool
        """

        # Execute the base class method.
        super(Sys_info_page, self).__init__(parent, sync=True)


    def add_contents(self, sizer):
        """Add the structure specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """


    def on_execute(self):
        """Execute the user function."""

        # Get the App.
        app = wx.GetApp()

        # First show the controller.
        app.gui.show_controller(None)

        # Go to the last line.
        app.gui.controller.log_panel.on_goto_end(None)

        # Wait a little while.
        sleep(0.5)

        # Finally, execute the user function.
        self.execute('sys_info')

        # Bring the controller to the front.
        wx.CallAfter(app.gui.controller.Raise)
