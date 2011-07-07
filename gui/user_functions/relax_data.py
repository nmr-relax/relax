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
"""The relaxation data user function GUI elements."""

# Python module imports.
from string import split

# relax module imports.
from generic_fns import pipes

# GUI module imports.
from base import UF_base, UF_page
from gui.paths import WIZARD_IMAGE_PATH
from gui.misc import gui_to_float, gui_to_int, gui_to_str
from gui.wizard import Wiz_window


# The container class.
class Relax_data(UF_base):
    """The container class for holding all GUI elements."""

    def delete(self, event):
        """The relax_data.delete user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=700, size_y=400, title=self.get_title('relax_data', 'delete'))
        page = Delete_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)
        wizard.run()


    def read(self, event):
        """The relax_data.read user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=1000, size_y=800, title=self.get_title('relax_data', 'read'))
        page = Read_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)
        wizard.run()



class Delete_page(UF_page):
    """The relax_data.read() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'fid.png'
    uf_path = ['relax_data', 'delete']

    def add_contents(self, sizer):
        """Add the relaxation data deletion specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The ID.
        self.ri_id = self.combo_box(sizer, "The relaxation data ID:", tooltip=self.uf._doc_args_dict['ri_id'])


    def on_execute(self):
        """Execute the user function."""

        # The labels and frq.
        ri_id = gui_to_str(self.ri_id.GetValue())

        # Read the relaxation data.
        self.interpreter.relax_data.delete(ri_id=ri_id)


    def on_display(self):
        """Clear previous data and update the label lists."""

        # Clear the previous data.
        self.ri_id.Clear()

        # No data, so don't try to fill the combo boxes.
        if not hasattr(cdp, 'ri_ids'):
            return

        # The relaxation data IDs.
        for i in range(len(cdp.ri_ids)):
            self.ri_id.Append(cdp.ri_ids[i])



class Read_page(UF_page):
    """The relax_data.read() user function page."""

    # Some class variables.
    desc_height = 140
    image_path = WIZARD_IMAGE_PATH + 'fid.png'
    uf_path = ['relax_data', 'read']

    def add_contents(self, sizer):
        """Add the relaxation data reading specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The relaxation data file:", title="Relaxation data file selection", tooltip=self.uf._doc_args_dict['file'])

        # The labels.
        self.ri_id = self.input_field(sizer, "The relaxation data ID:", tooltip=self.uf._doc_args_dict['ri_id'])
        self.ri_type = self.combo_box(sizer, "The relaxation data type:", choices=['R1', 'R2', 'NOE'], tooltip=self.uf._doc_args_dict['ri_type'])

        # The frequency.
        self.frq = self.input_field(sizer, "The proton frequency in Hz:", tooltip=self.uf._doc_args_dict['frq'])

        # The parameter file settings.
        self.free_file_format(sizer, data_cols=True, padding=5, spacer=0)

        # The spin ID restriction.
        self.spin_id = self.spin_id_element(sizer, desc="Restrict data loading to certain spins:")


    def on_execute(self):
        """Execute the user function."""

        # The labels and frq.
        ri_id = gui_to_str(self.ri_id.GetValue())
        ri_type = gui_to_str(self.ri_type.GetValue())
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
        self.interpreter.relax_data.read(ri_id=ri_id, ri_type=ri_type, frq=frq, file=file, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=err_col, sep=sep, spin_id=spin_id)
