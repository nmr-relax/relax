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

# Python module imports.
import wx
from wx.lib import buttons

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
        wizard = Wiz_window(size_x=700, size_y=600, title='Set parameter values')

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
    image_path = paths.IMAGE_PATH + 'relax.gif'
    main_text = 'Select one of the following analysis types.'
    title = 'Start a new analysis'

    def add_buttons(self, box):
        """The widget of analysis buttons.

        @param box:     A sizer object.
        @type box:      wx.BoxSizer instance
        """

        # The sizes.
        size = (150, 150)

        # The horizontal spacers.
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        # The NOE button.
        self.button_noe = wx.ToggleButton(self, -1, '')
        self.button_noe.SetToolTipString("Steady-state NOE analysis")
        self.button_noe.SetMinSize(size)
        sizer1.Add(self.button_noe)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.select_noe, self.button_noe)

        # The R1 button.
        self.button_r1 = wx.ToggleButton(self, -1, '')
        self.button_r1.SetToolTipString("R1 relaxation curve-fitting analysis")
        self.button_r1.SetMinSize(size)
        sizer1.Add(self.button_r1)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.select_r1, self.button_r1)

        # The R2 button.
        self.button_r2 = wx.ToggleButton(self, -1, '')
        self.button_r2.SetToolTipString("R2 relaxation curve-fitting analysis")
        self.button_r2.SetMinSize(size)
        sizer1.Add(self.button_r2)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.select_r2, self.button_r2)

        # The model-free button.
        self.button_mf = wx.ToggleButton(self, -1, '')
        self.button_mf.SetToolTipString("Model-free analysis")
        self.button_mf.SetMinSize(size)
        sizer2.Add(self.button_mf)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.select_mf, self.button_mf)

        # The custom analysis button.
        self.button_custom = wx.ToggleButton(self, -1, '')
        self.button_custom.SetToolTipString("Custom analysis")
        self.button_custom.SetMinSize(size)
        sizer2.Add(self.button_custom)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.select_custom, self.button_custom)

        # A blank button.
        self.button_none = wx.ToggleButton(self, -1, '')
        self.button_none.SetMinSize(size)
        sizer2.Add(self.button_none)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.select_none, self.button_none)

        # Add the sizers.
        box.Add(sizer1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        box.Add(sizer2, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)


    def add_contents(self, sizer):
        """Add the specific GUI elements (dummy method).

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add the button widget.
        self.add_buttons(sizer)


    def select_custom(self, event):
        """NOE analysis selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Toggle all buttons off.
        self.toggle(self.button_custom)

        # Set the analysis type.
        self.analysis_type = 'custom'


    def select_mf(self, event):
        """NOE analysis selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Toggle all buttons off.
        self.toggle(self.button_mf)

        # Set the analysis type.
        self.analysis_type = 'mf'


    def select_noe(self, event):
        """NOE analysis selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Toggle all buttons off.
        self.toggle(self.button_noe)

        # Set the analysis type.
        self.analysis_type = 'noe'


    def select_none(self, event):
        """No analysis selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Toggle all buttons off.
        self.toggle(self.button_none)

        # Set the analysis type.
        self.analysis_type = 'none'


    def select_r1(self, event):
        """NOE analysis selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Toggle all buttons off.
        self.toggle(self.button_r1)

        # Set the analysis type.
        self.analysis_type = 'r1'


    def select_r2(self, event):
        """NOE analysis selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Toggle all buttons off.
        self.toggle(self.button_r2)

        # Set the analysis type.
        self.analysis_type = 'r2'


    def toggle(self, button):
        """Toggle all buttons off except the selected one.

        @param button:  The button of the selected analysis.
        @type button:   wx.ToggleButton instance
        """

        # First freeze the wizard.
        self.Freeze()

        # Deselect all.
        self.button_noe.SetValue(False)
        self.button_r1.SetValue(False)
        self.button_r2.SetValue(False)
        self.button_mf.SetValue(False)
        self.button_custom.SetValue(False)
        self.button_none.SetValue(False)

        # Turn on the selected button.
        button.SetValue(True)

        # Refresh the GUI element.
        self.Refresh()

        # Unfreeze.
        self.Thaw()
