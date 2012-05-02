###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""The BMRB user function GUI elements."""

# Python module imports.
import wx

# GUI module imports.
from base import UF_base, UF_page
from gui.paths import WIZARD_IMAGE_PATH
from gui.misc import gui_to_float, gui_to_int, gui_to_str, str_to_gui


# The container class.
class Bmrb(UF_base):
    """The container class for holding all GUI elements."""

    def citation(self):
        """The bmrb.citation user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=1000, size_y=700, name='bmrb.citation', uf_page=Citation_page)
        wizard.run()



class Citation_page(UF_page):
    """The bmrb.citation() user function page."""

    # Some class variables.
    height_desc = 140
    image_path = WIZARD_IMAGE_PATH + 'bmrb.png'
    uf_path = ['bmrb', 'citation']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The fields.
        self.cite_id = self.input_field(sizer, "The citation ID:", tooltip=self.uf._doc_args_dict['cite_id'])
        self.authors = self.element_string_list_of_lists(key='authors', titles=["First name", "Last name", "First initial", "Middle initials"], sizer=sizer, desc="The author list:", tooltip=self.uf._doc_args_dict['authors'])


    def on_execute(self):
        """Execute the user function."""

        # The data.
        cite_id = gui_to_str(self.cite_id.GetValue())
        authors = self.GetValue('authors')

        # Read the relaxation data.
        self.execute('bmrb.citation', cite_id=cite_id, authors=authors)
