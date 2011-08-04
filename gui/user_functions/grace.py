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

# relax module imports.
from relax_errors import RelaxImplementError, RelaxNoPipeError
import specific_fns

# GUI module imports.
from base import UF_base, UF_page
from gui.errors import gui_raise
from gui.misc import gui_to_bool, gui_to_str, str_to_gui
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


    def write(self, event, file=None):
        """The grace.write user function.

        @param event:   The wx event.
        @type event:    wx event
        @keyword file:  The file to start the user function with.
        @type file:     str
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=1000, size_y=700, title=self.get_title('grace', 'write'))
        page = Write_page(wizard, self.gui)
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



class Write_page(UF_page):
    """The grace.write() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'grace.png'
    uf_path = ['grace', 'write']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The X-axis data.
        self.x_data_type = self.combo_box(sizer, "The X-axis data type:", tooltip=self.uf._doc_args_dict['x_data_type'])
        self.update_parameters(self.x_data_type)

        # The Y-axis data.
        self.y_data_type = self.combo_box(sizer, "The Y-axis data type:", tooltip=self.uf._doc_args_dict['y_data_type'])
        self.update_parameters(self.y_data_type)

        # The spin ID restriction.
        self.spin_id = self.spin_id_element(sizer, "Restrict plotting to certain spins:")

        # The plot data.
        self.plot_data = self.combo_box(sizer, "The plot data:", ['value', 'error', 'sims'], tooltip=self.uf._doc_args_dict['plot_data'], read_only=True)
        self.plot_data.SetValue('value')

        # Data normalisation.
        self.norm = self.boolean_selector(sizer, "Data normalisation flag:", tooltip=self.uf._doc_args_dict['norm'], default=False)

        # Add a file selection.
        self.file = self.file_selection(sizer, "The Grace file:", message="Grace file selection", wildcard="Grace files (*.agr)|*.agr", style=wx.FD_SAVE, tooltip=self.uf._doc_args_dict['file'])

        # The force flag.
        self.force = self.boolean_selector(sizer, "Force flag:", tooltip=self.uf._doc_args_dict['force'])


    def on_execute(self):
        """Execute the user function."""

        # The X and Y data types.
        x_data_type = self.x_data_type.GetClientData(self.x_data_type.GetSelection())
        y_data_type = self.y_data_type.GetClientData(self.y_data_type.GetSelection())

        # Get the values.
        spin_id =   gui_to_str(self.spin_id.GetValue())
        plot_data = gui_to_str(self.plot_data.GetValue())
        norm =      gui_to_bool(self.norm.GetValue())

        # The file name.
        file = gui_to_str(self.file.GetValue())
        if not file:
            return

        # Force flag.
        force = gui_to_bool(self.force.GetValue())

        # Open the file.
        self.gui.interpreter.grace.write(x_data_type=x_data_type, y_data_type=y_data_type, spin_id=spin_id, plot_data=plot_data, file=file, dir=None, force=force, norm=norm)


    def update_parameters(self, combo_box):
        """Fill out the list of parameters and their descriptions.

        @param combo_box:   The combo box element to update.
        @type combo_box:    wx.ComboBox instance
        """

        # Check the current data pipe.
        if cdp == None:
            gui_raise(RelaxNoPipeError())
            return

        # Get the specific functions.
        data_names = specific_fns.setup.get_specific_fn('data_names', cdp.pipe_type, raise_error=False)
        self.data_type = specific_fns.setup.get_specific_fn('data_type', cdp.pipe_type, raise_error=False)
        return_data_desc = specific_fns.setup.get_specific_fn('return_data_desc', cdp.pipe_type, raise_error=False)

        # The data names, if they exist.
        try:
            names = data_names(set='params')
        except RelaxImplementError:
            gui_raise(RelaxImplementError())
            return

        # First add the sequence data.
        combo_box.Append(str_to_gui("Spin sequence"), 'spin')

        # Loop over the parameters.
        for name in (data_names(set='params') + data_names(set='generic')):
            # Get the description.
            desc = return_data_desc(name)

            # No description.
            if not desc:
                text = name

            # The text.
            else:
                text = "'%s':  %s" % (name, desc)

            # Append the description.
            combo_box.Append(str_to_gui(text), name)

        # Default to the sequence.
        combo_box.SetSelection(0)
