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
"""The relaxation data user function GUI elements."""

# Python module imports.
from string import split
import wx

# relax module imports.
from generic_fns import pipes

# GUI module imports.
from base import UF_base, UF_window
from gui.paths import WIZARD_IMAGE_PATH
from gui.misc import gui_to_float, gui_to_int, gui_to_str


# The container class.
class Relax_data(UF_base):
    """The container class for holding all GUI elements."""

    def delete(self, event):
        """The relax_data.delete user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Initialise the dialog.
        window = Delete_window(self.gui, self.interpreter)

        # Show the dialog.
        window.ShowModal()

        # Destroy.
        window.Destroy()


    def read(self, event):
        """The relax_data.read user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Initialise the dialog.
        window = Read_window(self.gui, self.interpreter)

        # Show the dialog.
        window.ShowModal()

        # Destroy.
        window.Destroy()



class Delete_window(UF_window):
    """The relax_data.read() user function window."""

    # Some class variables.
    size_x = 600
    size_y = 400
    frame_title = 'Delete the relaxation data'
    image_path = WIZARD_IMAGE_PATH + 'fid.png'
    main_text = 'This dialog allows you to delete read relaxation data.'
    title = 'Relaxation data deletion'


    def add_uf(self, sizer):
        """Add the relaxation data deletion specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The data labels.
        self.ri_label = self.combo_box(sizer, "The relaxation data label:", choices=[])
        self.frq_label = self.combo_box(sizer, "The frequency label in MHz:", choices=[])


    def execute(self):
        """Execute the user function."""

        # The labels and frq.
        ri_label = gui_to_str(self.ri_label.GetValue())
        frq_label = gui_to_str(self.frq_label.GetValue())

        # Read the relaxation data.
        self.interpreter.relax_data.delete(ri_label=ri_label, frq_label=frq_label)


    def update(self, event):
        """Update the UI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous data.
        self.ri_label.Clear()
        self.frq_label.Clear()

        # No data, so don't try to fill the combo boxes.
        if not hasattr(cdp, 'ri_labels'):
            return

        # The relaxation data labels.
        for i in range(len(cdp.ri_labels)):
            self.ri_label.Append(cdp.ri_labels[i])

        # The frq labels.
        for i in range(len(cdp.frq_labels)):
            self.frq_label.Append(cdp.frq_labels[i])



class Read_window(UF_window):
    """The relax_data.read() user function window."""

    # Some class variables.
    size_x = 800
    size_y = 800
    frame_title = 'Read the relaxation data from a file'
    image_path = WIZARD_IMAGE_PATH + 'fid.png'
    main_text = 'This dialog allows you to read relaxation data from a file.'
    title = 'Relaxation data reading'


    def add_uf(self, sizer):
        """Add the relaxation data reading specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The relaxation data file:", title="Relaxation data file selection")

        # The data labels.
        self.ri_label = self.combo_box(sizer, "The relaxation data label:", choices=['R1', 'R2', 'NOE'], tooltip="This must be a unique identifier.")
        self.frq_label = self.input_field(sizer, "The frequency label in MHz:", tooltip="This must be a unique identifier.")

        # The frequency.
        self.frq = self.input_field(sizer, "The proton frequency in Hz:")

        # The parameter file settings.
        self.free_file_format(sizer, data_cols=True)

        # The spin ID restriction.
        self.spin_id = self.input_field(sizer, "Restrict data loading to certain spins:", tooltip="This must be a valid spin ID.  Multiple spins can be selected using ranges, the '|' operator, residue ranges, etc.")


    def execute(self):
        """Execute the user function."""

        # The labels and frq.
        ri_label = gui_to_str(self.ri_label.GetValue())
        frq_label = gui_to_str(self.frq_label.GetValue())
        frq = gui_to_float(self.frq.GetValue())

        # The file name.
        file = gui_to_str(self.file.GetValue())

        # No file.
        if not file:
            return

        # Get the column numbers.
        spin_id_col =   gui_to_int(self.spin_id_col.GetValue())
        mol_name_col =  gui_to_int(self.mol_name_col.GetValue())
        res_num_col =   gui_to_int(self.res_num_col.GetValue())
        res_name_col =  gui_to_int(self.res_name_col.GetValue())
        spin_num_col =  gui_to_int(self.spin_num_col.GetValue())
        spin_name_col = gui_to_int(self.spin_name_col.GetValue())
        data_col =      gui_to_int(self.data_col.GetValue())
        err_col =       gui_to_int(self.err_col.GetValue())

        # The column separator.
        sep = str(self.sep.GetValue())
        if sep == 'white space':
            sep = None

        # The spin ID.
        spin_id = gui_to_str(self.spin_id.GetValue())

        # Read the relaxation data.
        self.interpreter.relax_data.read(ri_label=ri_label, frq_label=frq_label, frq=frq, file=file, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=err_col, sep=sep, spin_id=spin_id)
