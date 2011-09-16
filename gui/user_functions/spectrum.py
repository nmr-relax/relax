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
"""The spectrum user function GUI elements."""

# Python module imports.
from os import sep
import wx

# GUI module imports.
from base import UF_base, UF_page
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.misc import gui_to_float, gui_to_int, gui_to_str, str_to_gui
from gui.paths import WIZARD_IMAGE_PATH


# The container class.
class Spectrum(UF_base):
    """The container class for holding all GUI elements."""

    def baseplane_rmsd(self):
        """The spectrum.baseplane_rmsd user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=800, size_y=500, name='spectrum.baseplane_rmsd', uf_page=Baseplane_rmsd_page)
        wizard.run()


    def delete(self, spectrum_id=None):
        """The spectrum.delete user function.

        @keyword spectrum_id:   The starting spectrum ID string.
        @type spectrum_id:      str
        """

        # Create the wizard.
        wizard, page = self.create_wizard(size_x=700, size_y=400, name='spectrum.delete', uf_page=Delete_page, return_page=True)

        # Default ID.
        if spectrum_id:
            page.spectrum_id.SetValue(str_to_gui(spectrum_id))

        # Execute the wizard.
        wizard.run()


    def error_analysis(self):
        """The spectrum.error_analysis user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=1000, size_y=700, name='spectrum.error_analysis', uf_page=Error_analysis_page, apply_button=False)
        wizard.run()


    def integration_points(self):
        """The spectrum.integration_points user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=800, size_y=600, name='spectrum.integration_points', uf_page=Integration_points_page)
        wizard.run()


    def read_intensities(self):
        """The spectrum.read_intensities user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=1000, size_y=800, name='spectrum.read_intensities', uf_page=Read_intensities_page)
        wizard.run()


    def replicated(self):
        """The spectrum.replicated user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=800, size_y=600, name='spectrum.replicated', uf_page=Replicated_page)
        wizard.run()



class Baseplane_rmsd_page(UF_page):
    """The spectrum.baseplane_rmsd() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'
    uf_path = ['spectrum', 'baseplane_rmsd']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The error.
        self.error = self.input_field(sizer, "The error:", tooltip=self.uf._doc_args_dict['error'])

        # The spectrum ID.
        self.spectrum_id = self.combo_box(sizer, "The spectrum ID:", tooltip=self.uf._doc_args_dict['spectrum_id'])

        # The spin ID restriction.
        self.spin_id = self.spin_id_element(sizer, desc="Restrict the error setting to certain spins:")


    def on_display(self):
        """Update the UI."""

        # Clear the previous data.
        self.spectrum_id.Clear()

        # Set the spectrum ID names.
        if hasattr(cdp, 'spectrum_ids'):
            for id in cdp.spectrum_ids:
                self.spectrum_id.Append(str_to_gui(id))


    def on_execute(self):
        """Execute the user function."""

        # Get the values.
        error = gui_to_float(self.error.GetValue())
        spectrum_id = gui_to_str(self.spectrum_id.GetValue())
        spin_id = gui_to_str(self.spin_id.GetValue())

        # Execute.
        interpreter.queue('spectrum.baseplane_rmsd', error=error, spectrum_id=spectrum_id, spin_id=spin_id)



class Delete_page(UF_page):
    """The spectrum.read() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'
    uf_path = ['spectrum', 'delete']

    def add_contents(self, sizer):
        """Add the spectral data deletion specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The ID.
        self.spectrum_id = self.combo_box(sizer, "The spectrum ID:", tooltip=self.uf._doc_args_dict['spectrum_id'])


    def on_execute(self):
        """Execute the user function."""

        # The ID.
        spectrum_id = gui_to_str(self.spectrum_id.GetValue())

        # Delete the spectral data.
        interpreter.queue('spectrum.delete', spectrum_id=spectrum_id)


    def on_display(self):
        """Clear previous data and update the label lists."""

        # Clear the previous data.
        self.spectrum_id.Clear()

        # No data, so don't try to fill the combo boxes.
        if not hasattr(cdp, 'spectrum_ids'):
            return

        # The spectrum IDs.
        for i in range(len(cdp.spectrum_ids)):
            self.spectrum_id.Append(str_to_gui(cdp.spectrum_ids[i]))



class Error_analysis_page(UF_page):
    """The spectrum.error_analysis() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'
    uf_path = ['spectrum', 'error_analysis']
    height_desc = 550

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

    def on_execute(self):
        """Execute the user function."""

        # Execute.
        interpreter.queue('spectrum.error_analysis')



class Integration_points_page(UF_page):
    """The spectrum.integration_points() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'
    uf_path = ['spectrum', 'integration_points']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The number of points.
        self.N = self.input_field(sizer, "The number of points:", tooltip=self.uf._doc_args_dict['N'])

        # The spectrum ID.
        self.spectrum_id = self.combo_box(sizer, "The spectrum ID:", tooltip=self.uf._doc_args_dict['spectrum_id'])

        # The spin ID restriction.
        self.spin_id = self.spin_id_element(sizer, desc="Restrict setting the number to certain spins:")


    def on_display(self):
        """Update the UI."""

        # Clear the previous data.
        self.spectrum_id.Clear()

        # Set the spectrum ID names.
        if hasattr(cdp, 'spectrum_ids'):
            for id in cdp.spectrum_ids:
                self.spectrum_id.Append(str_to_gui(id))


    def on_execute(self):
        """Execute the user function."""

        # Get the values.
        N = gui_to_int(self.N.GetValue())
        spectrum_id = gui_to_str(self.spectrum_id.GetValue())
        spin_id = gui_to_str(self.spin_id.GetValue())

        # Execute.
        interpreter.queue('spectrum.integration_points', N=N, spectrum_id=spectrum_id, spin_id=spin_id)



class Read_intensities_page(UF_page):
    """The spectrum.read_intensities() user function page."""

    # Some class variables.
    height_desc = 140
    image_path = WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'
    uf_path = ['spectrum', 'read_intensities']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The peak intensity file:", message="Peak intensity file selection", style=wx.FD_OPEN, tooltip=self.uf._doc_args_dict['file'])

        # The spectrum ID.
        self.spectrum_id = self.input_field(sizer, "The spectrum ID:", tooltip=self.uf._doc_args_dict['spectrum_id'])

        # The heteronucleus and proton.
        self.heteronuc = self.input_field(sizer, "The heternucleus name:", tooltip=self.uf._doc_args_dict['heteronuc'])
        self.proton = self.input_field(sizer, "The heternucleus name:", tooltip=self.uf._doc_args_dict['proton'])
        self.heteronuc.SetValue(str_to_gui('N'))
        self.proton.SetValue(str_to_gui('H'))

        # The integration method.
        self.int_method = self.combo_box(sizer, "The peak integration method:", tooltip=self.uf._doc_args_dict['int_method'], choices=['height', 'point sum', 'other'])
        self.int_method.SetValue(str_to_gui('height'))

        # The integration column.
        self.int_col = self.input_field(sizer, "The integration column:", tooltip=self.uf._doc_args_dict['int_col'])

        # The spin ID restriction.
        self.spin_id = self.spin_id_element(sizer, desc="Restrict data loading to certain spins:")

        # The integration column.
        self.ncproc = self.input_field(sizer, "The Bruker ncproc value:", tooltip=self.uf._doc_args_dict['ncproc'])

        # The parameter file settings.
        self.free_file_format(sizer, data_cols=False, padding=3, spacer=0)


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetValue())

        # The values.
        spectrum_id = gui_to_str(self.spectrum_id.GetValue())
        heteronuc = gui_to_str(self.heteronuc.GetValue())
        proton = gui_to_str(self.proton.GetValue())
        int_method = gui_to_str(self.int_method.GetValue())
        ncproc = gui_to_int(self.ncproc.GetValue())

        # Get the column numbers.
        int_col =       gui_to_int(self.int_col.GetValue())
        spin_id_col =   gui_to_int(self.spin_id_col.GetValue())
        mol_name_col =  gui_to_int(self.mol_name_col.GetValue())
        res_num_col =   gui_to_int(self.res_num_col.GetValue())
        res_name_col =  gui_to_int(self.res_name_col.GetValue())
        spin_num_col =  gui_to_int(self.spin_num_col.GetValue())
        spin_name_col = gui_to_int(self.spin_name_col.GetValue())

        # The column separator.
        sep = gui_to_str(self.sep.GetValue())
        if sep == 'white space':
            sep = None

        # The spin ID.
        spin_id = gui_to_str(self.spin_id.GetValue())

        # Read the peak intensities.
        interpreter.queue('spectrum.read_intensities', file=file, spectrum_id=spectrum_id, heteronuc=heteronuc, proton=proton, int_method=int_method, int_col=int_col, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, spin_id=spin_id, ncproc=ncproc)



class Replicated_page(UF_page):
    """The spectrum.replicated() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'
    uf_path = ['spectrum', 'replicated']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The spectrum IDs.
        self.spectrum_id_boxes = []
        self.spectrum_id_boxes.append(self.combo_box(sizer, "The 1st spectrum ID:", tooltip="The ID string of the first of the replicated spectra."))
        self.spectrum_id_boxes.append(self.combo_box(sizer, "The 2nd spectrum ID:", tooltip="The ID string of the second spectrum which is a replicate of the first spectrum."))
        self.spectrum_id_boxes.append(self.combo_box(sizer, "The 3rd spectrum ID:", tooltip="The ID string of the third spectrum which is a replicate of the first spectrum."))
        self.spectrum_id_boxes.append(self.combo_box(sizer, "The 4th spectrum ID:", tooltip="The ID string of the fourth spectrum which is a replicate of the first spectrum."))
        self.spectrum_id_boxes.append(self.combo_box(sizer, "The 5th spectrum ID:", tooltip="The ID string of the fifth spectrum which is a replicate of the first spectrum."))


    def on_display(self):
        """Update the UI."""

        # Loop over each box.
        for i in range(len(self.spectrum_id_boxes)):
            # First clear all data.
            self.spectrum_id_boxes[i].Clear()

            # Set the spectrum ID names.
            if hasattr(cdp, 'spectrum_ids'):
                for id in cdp.spectrum_ids:
                    self.spectrum_id_boxes[i].Append(str_to_gui(id))


    def on_execute(self):
        """Execute the user function."""

        # Loop over each box.
        spectrum_ids = []
        for i in range(len(self.spectrum_id_boxes)):
            # No selection (fix for Mac OS X).
            if self.spectrum_id_boxes[i].GetSelection() == -1:
                continue

            # Get the value.
            val = gui_to_str(self.spectrum_id_boxes[i].GetValue())

            # Add the value to the list if not None.
            if val != None:
                spectrum_ids.append(val)

        # Execute (only if more than one ID is given).
        if len(spectrum_ids) > 1:
            interpreter.queue('spectrum.replicated', spectrum_ids=spectrum_ids)
