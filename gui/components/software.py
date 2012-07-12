###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Michael Bieri                                       #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing the software GUI element for listing the software used in the analysis."""

# relax module imports.
from graphics import fetch_icon

# relax GUI module imports.
from gui.components.base_list import Base_list
from gui.string_conv import str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()


class Software(Base_list):
    """The GUI element for listing the software used in the analysis."""

    def action_bmrb_software(self, event):
        """Launch the bmrb.software user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Launch the dialog.
        uf_store['bmrb.software'](wx_parent=self.parent)


    def action_bmrb_software_select(self, event):
        """Launch the bmrb.software_select user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Launch the dialog.
        uf_store['bmrb.software_select'](wx_parent=self.parent)


    def setup(self):
        """Override the base variables."""

        # GUI variables.
        self.title = "Software"
        self.observer_base_name = "software"
        self.button_placement = 'bottom'

        # The column titles.
        self.columns = [
            "Program name"
        ]

        # Button set up.
        self.button_info = [
            {
                'object': 'button_add',
                'label': ' Add',
                'icon': fetch_icon('oxygen.actions.list-add-relax-blue', "22x22"),
                'method': self.action_bmrb_software,
                'tooltip': "Specify the software used in the analysis."
            }, {
                'object': 'button_select',
                'label': ' Select',
                'icon': fetch_icon('oxygen.actions.edit-select', "22x22"),
                'method': self.action_bmrb_software_select,
                'tooltip': "Select the software used in the analysis."
            }
        ]


    def update_data(self):
        """Method called from self.build_element_safe() to update the list data."""

        # Expand the number of rows to match the number of entries, and add the data.
        n = 0
        if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'software'):
            n = len(cdp.exp_info.software)
            for i in range(n):
                # Set the software name.
                self.element.InsertStringItem(i, str_to_gui(cdp.exp_info.software[i].name))
