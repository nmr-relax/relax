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
import specific_fns

# GUI module imports.
from base import UF_base, UF_panel
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
        wizard = Wiz_window(size_x=800, size_y=600, title='Set parameter values')
        wizard.add_page(Set_panel(self))
        wizard.run()



class Set_panel(UF_panel):
    """The user function window."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'value' + sep + 'value.png'
    main_text = 'This dialog allows you to set spin specific data values.'
    title = 'Value setting'


    def add_contents(self, sizer):
        """Add the sequence specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The parameter.
        self.param = self.input_field(sizer, "The parameter:")

        # The value.
        self.value = self.input_field(sizer, "The value:")

        # The spin ID restriction.
        self.spin_id = self.input_field(sizer, "Restrict data loading to certain spins:", tooltip="This must be a valid spin ID.  Multiple spins can be selected using ranges, the '|' operator, residue ranges, etc.")


    def execute(self):
        """Execute the user function."""

        # The parameter and value.
        param = gui_to_str(self.param.GetValue())
        value = gui_to_str(self.value.GetValue())

        # The spin ID.
        spin_id = gui_to_str(self.spin_id.GetValue())

        # Set the value.
        self.interpreter.value.set(val=value, param=param, spin_id=spin_id)


    def update(self, event):
        """Update the UI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Get the specific functions.
        data_names = specific_fns.setup.get_specific_fn('data_names', pipes.get_type(), raise_error=False)
        return_data_desc = specific_fns.setup.get_specific_fn('return_data_desc', pipes.get_type(), raise_error=False)

        # Loop over the parameters.
        #for name in data_names(set='params'):
        #    # Get the description.
        #    desc = return_data_desc(name)

        #    # No description.
        #    if not desc:
        #        desc = name

        #    # Append the description.
        #    self.param.Append(str_to_gui(desc), name)

