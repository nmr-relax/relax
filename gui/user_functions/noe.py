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
"""The noe user function GUI elements."""

# Python module imports.
from os import sep
from string import split
import wx

# relax module imports.
from generic_fns import pipes

# GUI module imports.
from base import UF_base, UF_page
from gui.paths import ANALYSIS_IMAGE_PATH
from gui.misc import gui_to_float, gui_to_int, gui_to_str, str_to_gui
from gui.wizard import Wiz_window


# The container class.
class Noe(UF_base):
    """The container class for holding all GUI elements."""

    def read_restraints(self, event):
        """The noe.read_restraints user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title=self.get_title('noe', 'read_restraints'))
        page = Read_restraints_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()


    def spectrum_type(self, event):
        """The noe.spectrum_type user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title=self.get_title('noe', 'spectrum_type'))
        page = Spectrum_type_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()



class Read_restraints_page(UF_page):
    """The noe.read_restraints() user function page."""

    # Some class variables.
    image_path = ANALYSIS_IMAGE_PATH + 'noe_200x200.png'
    uf_path = ['noe', 'read_restraints']

    def add_contents(self, sizer):
        """Add the page specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The restraint file:", message="Restraint file selection", style=wx.FD_OPEN, tooltip=self.uf._doc_args_dict['file'])

        # The columns.
        self.proton1_col = self.input_field(sizer, "The 1st proton column:", tooltip=self.uf._doc_args_dict['proton1_col'])
        self.proton2_col = self.input_field(sizer, "The 2nd proton column:", tooltip=self.uf._doc_args_dict['proton2_col'])
        self.lower_col = self.input_field(sizer, "The lower bound column:", tooltip=self.uf._doc_args_dict['lower_col'])
        self.upper_col = self.input_field(sizer, "The upper bound column:", tooltip=self.uf._doc_args_dict['upper_col'])

        # The column separator.
        self.sep = self.combo_box(sizer, "Column separator:", ["white space", ",", ";", ":", ""], read_only=False)

        # Spacing.
        sizer.AddStretchSpacer()


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetValue())

        # No file.
        if not file:
            return

        # Get the column numbers.
        proton1_col =   gui_to_int(self.proton1_col.GetValue())
        proton2_col =   gui_to_int(self.proton2_col.GetValue())
        lower_col =     gui_to_int(self.lower_col.GetValue())
        upper_col =     gui_to_int(self.upper_col.GetValue())

        # The column separator.
        sep = str(self.sep.GetValue())
        if sep == 'white space':
            sep = None

        # Read the NOESY data.
        self.gui.interpreter.noe.read_restraints(file=file, proton1_col=proton1_col, proton2_col=proton2_col, lower_col=lower_col, upper_col=upper_col, sep=sep)



class Spectrum_type_page(UF_page):
    """The noe.spectrum_type() user function page."""

    # Some class variables.
    image_path = ANALYSIS_IMAGE_PATH + 'noe_200x200.png'
    uf_path = ['noe', 'spectrum_type']

    def add_contents(self, sizer):
        """Add the page specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The spectrum type.
        self.spectrum_type = self.combo_box(sizer, "The spectrum type:", tooltip=self.uf._doc_args_dict['spectrum_type'], choices=['Saturated spectrum', 'Reference spectrum'])
        self.spectrum_type.SetClientData(0, 'sat')
        self.spectrum_type.SetClientData(1, 'ref')

        # The spectrum ID.
        self.spectrum_id = self.combo_box(sizer, "The spectrum ID:", tooltip=self.uf._doc_args_dict['spectrum_id'])

        # Spacing.
        sizer.AddStretchSpacer()


    def on_execute(self):
        """Execute the user function."""

        # The values.
        spectrum_type = gui_to_str(self.spectrum_type.GetClientData(self.spectrum_type.GetSelection()))

        # The spectrum ID.
        spectrum_id = gui_to_str(self.spectrum_id.GetValue())

        # Read the relaxation data.
        self.gui.interpreter.noe.spectrum_type(spectrum_type=spectrum_type, spectrum_id=spectrum_id)


    def on_display(self):
        """Clear previous data and update the spectrum ID list."""

        # Clear the previous data.
        self.spectrum_id.Clear()

        # No data, so don't try to fill the combo box.
        if not hasattr(cdp, 'spectrum_ids'):
            return

        # The spectrum IDs.
        for i in range(len(cdp.spectrum_ids)):
            self.spectrum_id.Append(str_to_gui(cdp.spectrum_ids[i]))
