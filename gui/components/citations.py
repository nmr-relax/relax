###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Michael Bieri                                       #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
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
"""Module containing the citations GUI element for listing the citations relevant for the analysis."""

# relax module imports.
from graphics import fetch_icon

# relax GUI module imports.
from gui.components.base_list import Base_list
from gui.string_conv import str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()


class Citations(Base_list):
    """The GUI element for listing the citations relevant for the analysis."""

    def action_bmrb_citation(self, event):
        """Launch the bmrb.citation user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Launch the dialog.
        uf_store['bmrb.citation'](wx_parent=self.parent)


    def setup(self):
        """Override the base variables."""

        # GUI variables.
        self.title = "Citations"
        self.observer_base_name = "citations"
        self.button_placement = 'bottom'

        # The column titles.
        self.columns = [
            "Citation ID"
        ]

        # Button set up.
        self.button_info = [
            {
                'object': 'button_add',
                'label': ' Add',
                'icon': fetch_icon('oxygen.actions.list-add-relax-blue', "22x22"),
                'method': self.action_bmrb_citation,
                'tooltip': "Specify a citation to be added the BMRB data file."
            }
        ]


    def update_data(self):
        """Method called from self.build_element_safe() to update the list data."""

        # Expand the number of rows to match the number of entries, and add the data.
        n = 0
        if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'citations'):
            n = len(cdp.exp_info.citations)
            for i in range(n):
                # Set the citation ID.
                self.element.InsertStringItem(i, str_to_gui(cdp.exp_info.citations[i].cite_id))
