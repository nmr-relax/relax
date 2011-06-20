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
"""Module for the analysis selection wizard."""

# relax GUI module imports.
from gui import paths
from gui.wizard import Wiz_panel, Wiz_window


class Analysis_wizard:
    """The analysis selection wizard."""

    def run(self):
        """Run through the analysis selection wizard, returning the results.

        @return:    The analysis type and data pipe name.
        @rtype:     str, str
        """

        # Set up the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title='Set parameter values')

        # Add the new analysis panel.
        new_panel = New_analysis_panel(wizard)
        wizard.add_page(new_panel, apply_button=False)

        # Add the data pipe name panel.
        pipe_panel = Data_pipe_panel(wizard)
        wizard.add_page(pipe_panel, apply_button=False)

        # Execute the wizard.
        wizard.run()

        # Return the analysis type and pipe name.
        return new_panel.analysis_type, str(pipe_panel.pipe_name.GetValue())



class Data_pipe_panel(Wiz_panel):
    """The panel for setting the data pipe name."""

    # Class variables.
    pipe_name = 'x'
    image_path = paths.WIZARD_IMAGE_PATH + 'pipe.png'
    main_text = 'Select the name of the pipe name to be associated with the analysis'
    title = 'Data pipe name'

    def add_contents(self, sizer):
        """Add the specific GUI elements (dummy method).

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The pipe name input.
        self.pipe_name = self.input_field(sizer, "The data pipe name:")


    def update(self, event):
        """Update the UI.

        @param event:   The wx event.
        @type event:    wx event
        """

        self.pipe_name.SetValue('test')



class New_analysis_panel(Wiz_panel):
    """The panel for selection of the new analysis."""

    # Class variables.
    analysis_type = 'mf'
    image_path = paths.IMAGE_PATH + 'relax.gif'
    main_text = 'Select one of the following analysis types.'
    title = 'Start a new analysis'

    def add_contents(self, sizer):
        """Add the specific GUI elements (dummy method).

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

