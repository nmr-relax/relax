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
from relax_errors import RelaxError, RelaxImplementError, RelaxNoPipeError
import specific_fns

# GUI module imports.
from base import UF_base, UF_page
from gui.errors import gui_raise
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.misc import gui_to_str, str_to_gui
from gui.paths import WIZARD_IMAGE_PATH
from gui.wizard import Wiz_window


# The container class.
class Value(UF_base):
    """The container class for holding all GUI elements."""

    def set(self, event, param=None):
        """The value.set user function.

        @param event:   The wx event.
        @type event:    wx event
        @keyword param: The starting parameter.
        @type param:    str
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=1000, size_y=800, title=self.get_title('value', 'set'))
        page = Set_page(wizard)
        wizard.add_page(page)

        # Default parameter.
        page.set_param(param)

        # Execute the wizard.
        wizard.run()



class Set_page(UF_page):
    """The value.set() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'value' + sep + 'value.png'
    uf_path = ['value', 'set']
    height_desc = 400

    def add_contents(self, sizer):
        """Add the sequence specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The parameter.
        self.param = self.combo_box(sizer, "The parameter:", tooltip=self.uf._doc_args_dict['param'], evt_fn=self.set_default_value)
        self.update_parameters()

        # The value.
        self.val = self.input_field(sizer, "The value:", tooltip=self.uf._doc_args_dict['val'])

        # The spin ID restriction.
        self.spin_id = self.spin_id_element(sizer, "Restrict value setting to certain spins:")


    def on_execute(self):
        """Execute the user function."""

        # The parameter.
        param = self.param.GetClientData(self.param.GetSelection())

        # The value (converted to the correct type).
        val_str = gui_to_str(self.val.GetValue())
        val_type = self.data_type(param)

        # Evaluate numbers.
        if val_type in [float, int]:
            fn = eval
        else:
            fn = val_type

        # Convert.
        try:
            val = fn(val_str)
        except (ValueError, NameError):
            gui_raise(RelaxError("The value '%s' should be of the type %s." % (val_str, val_type)), raise_flag=False)
            return

        # The spin ID.
        spin_id = gui_to_str(self.spin_id.GetValue())

        # Set the value.
        interpreter.queue('value.set', val=val, param=param, spin_id=spin_id)


    def set_default_value(self, event=None):
        """Set the value to the default once a parameter is selected.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The parameter.
        param = self.param.GetClientData(self.param.GetSelection())

        # Clear the previous data.
        self.val.Clear()

        # Nothing to do.
        if param == '':
            return

        # Get the default value.
        default_value = specific_fns.setup.get_specific_fn('default_value', cdp.pipe_type, raise_error=False)
        value = default_value(param)

        # Set the default value.
        if value != None:
            self.val.SetValue(str_to_gui(str(value)))


    def set_param(self, param):
        """Set the selection to the given parameter.

        @keyword param: The starting parameter.
        @type param:    str
        """

        # Nothing to do.
        if param == None:
            return

        # Find the parameter in the list.
        for i in range(self.param.GetCount()):
            if param == self.param.GetClientData(i):
                self.param.SetSelection(i)

        # Set the default value.
        self.set_default_value()


    def update_parameters(self):
        """Fill out the list of parameters and their descriptions."""

        # Check the current data pipe.
        if cdp == None:
            gui_raise(RelaxNoPipeError())
            self.setup_fail = True
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
            self.setup_fail = True
            return

        # Clear the previous data.
        self.param.Clear()

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
            self.param.Append(str_to_gui(text), name)
