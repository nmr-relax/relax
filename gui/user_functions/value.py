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
from os import sep

# relax module imports.
from generic_fns import pipes
from relax_errors import RelaxImplementError, RelaxNoPipeError
import specific_fns

# GUI module imports.
from base import UF_base, UF_page
from gui.errors import gui_raise
from gui.misc import gui_to_str, str_to_gui
from gui.paths import WIZARD_IMAGE_PATH
from gui.wizard import Wiz_window


# The container class.
class Value(UF_base):
    """The container class for holding all GUI elements."""

    def set(self, event):
        """The value.set user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=1000, size_y=800, title=self.get_title('value', 'set'))
        page = Set_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)
        wizard.run()



class Set_page(UF_page):
    """The value.set() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'value' + sep + 'value.png'
    uf_path = ['value', 'set']
    desc_height = 400

    def add_contents(self, sizer):
        """Add the sequence specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The parameter.
        self.param = self.combo_box(sizer, "The parameter:", tooltip=self.uf._doc_args_dict['param'])

        # The value.
        self.val = self.input_field(sizer, "The value:", tooltip=self.uf._doc_args_dict['val'])

        # The spin ID restriction.
        self.spin_id = self.spin_id_element(sizer, "Restrict value setting to certain spins:")


    def on_display(self):
        """Fill out the list of parameters and their descriptions."""

        # Check the current data pipe.
        if cdp == None:
            gui_raise(RelaxNoPipeError())

        # Get the specific functions.
        data_names = specific_fns.setup.get_specific_fn('data_names', cdp.pipe_type, raise_error=False)
        return_data_desc = specific_fns.setup.get_specific_fn('return_data_desc', cdp.pipe_type, raise_error=False)

        # The data names, if they exist.
        try:
            names = data_names(set='params')
        except RelaxImplementError:
            gui_raise(RelaxImplementError())

        # Loop over the parameters.
        for name in data_names(set='params'):
            # Get the description.
            desc = return_data_desc(name)

            # No description.
            if not desc:
                text = name

            # The text.
            else:
                text = "%s:  %s" % (name, desc)

            # Append the description.
            self.param.Append(str_to_gui(text), name)


    def on_execute(self):
        """Execute the user function."""

        # The parameter and value.
        param = gui_to_str(self.param.GetValue())
        val = gui_to_str(self.val.GetValue())

        # The spin ID.
        spin_id = gui_to_str(self.spin_id.GetValue())

        # Set the value.
        self.interpreter.value.set(val=val, param=param, spin_id=spin_id)
