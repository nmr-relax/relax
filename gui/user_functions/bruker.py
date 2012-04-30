###############################################################################
#                                                                             #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
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
"""The Bruker Dynamics Center user function GUI elements."""

# Python module imports.
from string import split
import wx

# relax module imports.
from generic_fns import pipes

# GUI module imports.
from base import UF_base, UF_page
from gui.paths import WIZARD_IMAGE_PATH
from gui.misc import gui_to_float, gui_to_int, gui_to_str, str_to_gui


# The container class.
class Bruker(UF_base):
    """The container class for holding all GUI elements."""

    def read(self):
        """The bruker.read user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=800, size_y=500, name='bruker.read', uf_page=Read_page)
        wizard.run()



class Read_page(UF_page):
    """The bruker.read() user function page."""

    # Some class variables.
    height_desc = 140
    image_path = WIZARD_IMAGE_PATH + 'bruker.png'
    uf_path = ['bruker', 'read']

    def add_contents(self, sizer):
        """Add the Bruker Dynamics Center reading specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The Bruker Dynamics Center file:", message="Bruker Dynamics Center file selection", style=wx.FD_OPEN, tooltip=self.uf._doc_args_dict['file'])

        # The labels.
        self.ri_id = self.input_field(sizer, "The relaxation data ID:", tooltip=self.uf._doc_args_dict['ri_id'])


    def on_execute(self):
        """Execute the user function."""

        # The labels and frq.
        ri_id = gui_to_str(self.ri_id.GetValue())

        # The file name.
        file = gui_to_str(self.file.GetValue())

        # No file.
        if not file:
            return

        # Read the Bruker data.
        self.execute('bruker.read', ri_id=ri_id, file=file)
