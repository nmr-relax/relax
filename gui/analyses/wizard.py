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
from os import sep
from time import asctime, localtime
import wx
from wx.lib import buttons

# relax GUI module imports.
from gui import paths
from gui.misc import gui_to_str, str_to_gui
from gui.wizard import Wiz_page, Wiz_window


class Analysis_wizard:
    """The analysis selection wizard."""

    def run(self):
        """Run through the analysis selection wizard, returning the results.

        @return:    The analysis type, analysis name, and data pipe name.
        @rtype:     tuple of str
        """

        # Set up the wizard.
        self.wizard = Wiz_window(size_x=850, size_y=700, title='Set parameter values')

        # Add the new analysis panel.
        new_page = New_analysis_page(self.wizard)
        self.wizard.add_page(new_page, apply_button=False)

        # Add the data pipe name panel.
        pipe_page = Data_pipe_page(self.wizard)
        self.wizard.add_page(pipe_page, apply_button=False)

        # Execute the wizard.
        setup = self.wizard.run(modal=True)
        if not setup:
            return

        # Get the data.
        analysis_type = self.wizard.analysis_type
        analysis_name = gui_to_str(new_page.analysis_name.GetValue())
        pipe_name = gui_to_str(pipe_page.pipe_name.GetValue())

        # Return the analysis type and pipe name.
        return analysis_type, analysis_name, pipe_name



class Data_pipe_page(Wiz_page):
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


    def on_display(self):
        """Update the pipe name."""

        # Generate a name for the data pipe based on the type and time.
        name = "%s (%s)" % (self.parent.analysis_type, asctime(localtime()))

        # Update the field.
        self.pipe_name.SetValue(str_to_gui(name))



class New_analysis_button(buttons.ThemedGenBitmapTextToggleButton):
    """A special button for the new analysis panel."""

    def OnLeftDown(self, event):
        """Catch left button mouse down events to ignore when the button is toggled.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Do nothing on a click if already selected.
        if self.GetValue():
            event.Skip()

        # Otherwise, perform the normal operations.
        else:
            super(buttons.ThemedGenBitmapTextToggleButton, self).OnLeftDown(event)


    def OnMouse(self, event):
        """Catch mouse events, specifically entry into the window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Do nothing if entering the button when it is selected.
        if event.GetEventType() == wx.EVT_ENTER_WINDOW.typeId and self.GetValue():
            event.Skip()

        # Otherwise, perform the normal operations.
        else:
            super(buttons.ThemedGenBitmapTextToggleButton, self).OnMouse(event)



class New_analysis_page(Wiz_page):
    """The panel for selection of the new analysis."""

    # Class variables.
    image_path = paths.IMAGE_PATH + "relax.gif"
    main_text = "A number of automatic analyses to be preformed using relax in GUI mode.  Although not as flexible or powerful as the prompt/scripting modes, this provides a quick and easy setup and execution for a number of analysis types.   These currently include the calculation of the steady-state NOE, the exponential curve-fitting for the R1 and R2 relaxation rates, and for a full and automatic model-free analysis using the d'Auvergne and Gooley, 2008b protocol.  All analyses perform error propagation using the gold standard Monte Calro simulations.  Please select from one of the following analysis types:"
    title = "Start a new analysis"

    def add_artwork(self, sizer):
        """Add the artwork to the dialog.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Create a vertical box.
        sizer2 = wx.BoxSizer(wx.VERTICAL)

        # Add a spacer.
        sizer2.AddSpacer(30)

        # Add the graphics.
        self.image = wx.StaticBitmap(self, -1, wx.Bitmap(self.image_path, wx.BITMAP_TYPE_ANY))
        sizer2.Add(self.image, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Nest the sizers.
        sizer.Add(sizer2)

        # A spacer.
        sizer.AddSpacer(self.art_spacing)


    def add_buttons(self, box):
        """The widget of analysis buttons.

        @param box:     A sizer object.
        @type box:      wx.BoxSizer instance
        """

        # The sizes.
        size = (170, 170)

        # No button is initially selected.
        self._select_flag = False

        # The horizontal spacers.
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        # A set of unique IDs for the buttons.
        self.button_ids = {'noe': wx.NewId(),
                           'r1': wx.NewId(),
                           'r2': wx.NewId(),
                           'consist_test': wx.NewId(),
                           'mf': wx.NewId(),
                           'custom': wx.NewId()}

        # The NOE button.
        self.button_noe = self.create_button(id=self.button_ids['noe'], box=sizer1, size=size, bmp=paths.ANALYSIS_IMAGE_PATH+"noe_150x150.png", tooltip="Steady-state NOE analysis", fn=self.select_noe)

        # The R1 button.
        self.button_r1 = self.create_button(id=self.button_ids['r1'], box=sizer1, size=size, bmp=paths.ANALYSIS_IMAGE_PATH+"r1_150x150.png", tooltip="R1 relaxation curve-fitting analysis", fn=self.select_r1)

        # The R2 button.
        self.button_r2 = self.create_button(id=self.button_ids['r2'], box=sizer1, size=size, bmp=paths.ANALYSIS_IMAGE_PATH+"r2_150x150.png", tooltip="R2 relaxation curve-fitting analysis", fn=self.select_r2)

        # Consistency testing.
        self.button_consist_test = self.create_button(id=self.button_ids['consist_test'], box=sizer2, size=size, bmp=paths.ANALYSIS_IMAGE_PATH+"consistency_testing_150x70.png", tooltip="Relaxation data consistency testing", fn=self.select_consist_test, disabled=True)

        # The model-free button.
        self.button_mf = self.create_button(id=self.button_ids['mf'], box=sizer2, size=size, bmp=paths.ANALYSIS_IMAGE_PATH+"model_free"+sep+"model_free_150x150.png", tooltip="Model-free analysis", fn=self.select_mf)

        # The custom analysis button.
        self.button_custom = self.create_button(id=self.button_ids['custom'], box=sizer2, size=size, bmp=paths.ANALYSIS_IMAGE_PATH+"custom_150x150.png", tooltip="Custom analysis", fn=self.select_custom, disabled=True)

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

        # Add a spacer.
        sizer.AddStretchSpacer(2)

        # Add the analysis name field.
        self.analysis_name = self.input_field(sizer, "The name of the new analysis:", tooltip='The name of the analysis can be changed to any text.')


    def create_button(self, id=-1, box=None, size=None, bmp=None, text='', tooltip='', fn=None, disabled=False):
        """Create a button for the new analysis selector panel.

        @keyword id:        The unique ID number.
        @type id:           int
        @keyword box:       The box sizer to place the button into.
        @type box:          wx.BoxSizer instance
        @keyword size:      The size of the button.
        @type size:         tuple of int
        @keyword bmp:       The full path of the bitmap image to use for the button.
        @type bmp:          str
        @keyword text:      The text for the button.
        @type text:         str
        @keyword tooltip:   The button tooltip text.
        @type tooltip:      str
        @keyword fn:        The function to bind the button click to.
        @type fn:           method
        @return:            The button.
        @rtype:             wx.lib.buttons.ThemedGenBitmapTextToggleButton instance
        """

        # Generate the button.
        if bmp:
            image = wx.Bitmap(bmp, wx.BITMAP_TYPE_ANY)
            button = New_analysis_button(self, id, image)
        else:
            button = New_analysis_button(self, id)

        # Set the tool tip.
        button.SetToolTipString(tooltip)

        # Button properties.
        button.SetMinSize(size)

        # Add to the given sizer.
        box.Add(button)

        # Bind the click.
        self.Bind(wx.EVT_BUTTON, fn, button)

        # The button is disabled.
        if disabled:
            button.Disable()

        # Return the button.
        return button


    def on_display(self):
        """Disable the next button until an analysis is selected."""

        # Turn off the next button.
        self.parent.block_next(not self._select_flag)


    def select_consist_test(self, event):
        """NOE analysis selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Toggle all buttons off.
        self.toggle(self.button_consist_test)

        # Set the analysis type.
        self.parent.analysis_type = 'consistency test'


    def select_custom(self, event):
        """NOE analysis selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Toggle all buttons off.
        self.toggle(self.button_custom)

        # Set the analysis type.
        self.parent.analysis_type = 'custom'


    def select_mf(self, event):
        """NOE analysis selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Toggle all buttons off.
        self.toggle(self.button_mf)

        # Update the analysis name.
        self.analysis_name.SetValue(str_to_gui('Model-free'))

        # Set the analysis type.
        self.parent.analysis_type = 'mf'


    def select_noe(self, event):
        """NOE analysis selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Toggle all buttons off.
        self.toggle(self.button_noe)

        # Update the analysis name.
        self.analysis_name.SetValue(str_to_gui('Steady-state NOE'))

        # Set the analysis type.
        self.parent.analysis_type = 'noe'


    def select_r1(self, event):
        """NOE analysis selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Toggle all buttons off.
        self.toggle(self.button_r1)

        # Update the analysis name.
        self.analysis_name.SetValue(str_to_gui('R1 relaxation'))

        # Set the analysis type.
        self.parent.analysis_type = 'r1'


    def select_r2(self, event):
        """NOE analysis selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Toggle all buttons off.
        self.toggle(self.button_r2)

        # Update the analysis name.
        self.analysis_name.SetValue(str_to_gui('R2 relaxation'))

        # Set the analysis type.
        self.parent.analysis_type = 'r2'


    def toggle(self, button):
        """Toggle all buttons off except the selected one.

        @param button:  The button of the selected analysis.
        @type button:   wx.ToggleButton instance
        """

        # First freeze the wizard.
        self.Freeze()

        # The button is selected.
        self._select_flag = True

        # Deselect all.
        self.button_noe.SetValue(False)
        self.button_r1.SetValue(False)
        self.button_r2.SetValue(False)
        self.button_consist_test.SetValue(False)
        self.button_mf.SetValue(False)
        self.button_custom.SetValue(False)

        # Turn on the selected button.
        button.SetValue(True)

        # Refresh the GUI element.
        self.Refresh()

        # Unfreeze.
        self.Thaw()

        # Unblock forwards movement.
        self.parent.block_next(not self._select_flag)
