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
from gui.misc import gui_to_float, gui_to_int, gui_to_str, str_to_gui
from gui.wizard import Wiz_window


# The container class.
class Relax_fit(UF_base):
    """The container class for holding all GUI elements."""

    def relax_time(self, event):
        """The relax_fit.relax_time user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title=self.get_title('relax_fit', 'relax_time'))
        page = Relax_time_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()


    def select_model(self, event):
        """The relax_fit.select_model user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title=self.get_title('relax_fit', 'select_model'))
        page = Select_model_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()



class Relax_time_page(UF_page):
    """The relax_fit.relax_time() user function page."""

    # Some class variables.
    uf_path = ['relax_fit', 'relax_time']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The time.
        self.time = self.input_field(sizer, "The delay time:", tooltip=self.uf._doc_args_dict['time'])

        # The spectrum ID.
        self.spectrum_id = self.combo_box(sizer, "The spectrum ID:", tooltip=self.uf._doc_args_dict['spectrum_id'])

        # Spacing.
        sizer.AddStretchSpacer()


    def on_execute(self):
        """Execute the user function."""

        # The time.
        time = gui_to_float(self.time.GetValue())

        # The spectrum ID.
        spectrum_id = gui_to_str(self.spectrum_id.GetStringSelection())

        # Read the relaxation data.
        self.gui.interpreter.queue('relax_fit.relax_time', time=time, spectrum_id=spectrum_id)


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



class Select_model_page(UF_page):
    """The relax_fit.select_model() user function page."""

    # Some class variables.
    uf_path = ['relax_fit', 'select_model']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The model.
        self.model = self.combo_box(sizer, "The model:", choices=['exp', 'inv'], tooltip=self.uf._doc_args_dict['model'])
        self.model.SetValue(str_to_gui('exp'))

        # Spacing.
        sizer.AddStretchSpacer()


    def on_execute(self):
        """Execute the user function."""

        # The model.
        model = gui_to_str(self.model.GetValue())

        # Read the relaxation data.
        self.gui.interpreter.queue('relax_fit.select_model', model=model)
