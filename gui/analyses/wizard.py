###############################################################################
#                                                                             #
# Copyright (C) 2011-2013 Edward d'Auvergne                                   #
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
"""Module for the analysis selection wizard."""

# Python module imports.
from os import sep
from time import asctime, localtime
import wx
from wx.lib import buttons

# relax module imports.
from graphics import ANALYSIS_IMAGE_PATH, IMAGE_PATH, WIZARD_IMAGE_PATH
from gui.input_elements.value import Value
from gui.misc import bitmap_setup
from gui.string_conv import gui_to_str, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from gui.wizards.wiz_objects import Wiz_page, Wiz_window


class Analysis_wizard:
    """The analysis selection wizard."""

    def run(self):
        """Run through the analysis selection wizard, returning the results.

        @return:    The analysis type, analysis name, data pipe name, data pipe bundle name, and user function on_execute method list.
        @rtype:     tuple of str
        """

        # Change the cursor to busy.
        wx.Yield()
        wx.BeginBusyCursor()

        # Set up the wizard.
        self.wizard = Wiz_window(size_x=1000, size_y=700, title='Analysis selection wizard')

        # Change the finish button.
        self.wizard.TEXT_FINISH = " Start"

        # Add the new analysis panel.
        self.new_page = New_analysis_page(self.wizard)
        self.wizard.add_page(self.new_page, apply_button=False)
        self.wizard.set_seq_next_fn(0, self.wizard_page_after_analysis)

        # The relax_disp.exp_type page.
        self.relax_disp_page = uf_store['relax_disp.exp_type'].create_page(self.wizard, sync=True, execute=False)
        self.wizard.add_page(self.relax_disp_page, apply_button=False)

        # Add the data pipe name panel.
        self.pipe_page = Data_pipe_page(self.wizard, height_desc=400)
        self.wizard.add_page(self.pipe_page, apply_button=False)

        # Reset the cursor.
        if wx.IsBusy():
            wx.EndBusyCursor()

        # Execute the wizard.
        setup = self.wizard.run(modal=True)
        if setup != wx.ID_OK:
            return

        # Return the analysis type, analysis name, data pipe name, data pipe bundle name, and user function on_execute method list.
        return self.get_data()


    def get_data(self):
        """Assemble and return the analysis type, analysis name, and pipe name.

        @return:    The analysis type, analysis name, data pipe name, data pipe bundle name, and list of user function on_execute methods.
        @rtype:     str, str, str, str, list of methods
        """

        # Get the data.
        analysis_type = gui_to_str(self.wizard.analysis_type)
        analysis_name = gui_to_str(self.new_page.analysis_name.GetValue())
        pipe_name = gui_to_str(self.pipe_page.pipe_name.GetValue())
        pipe_bundle = gui_to_str(self.pipe_page.pipe_bundle.GetValue())

        # The user function on_execute methods.
        uf_exec = []
        if analysis_name == 'Relaxation dispersion':
            uf_exec.append(self.relax_disp_page.on_execute)

        # Return it.
        return analysis_type, analysis_name, pipe_name, pipe_bundle, uf_exec


    def wizard_page_after_analysis(self):
        """Set the page after the data pipe setup.

        @return:    The index of the next page, which is the current page index plus one.
        @rtype:     int
        """

        # The selected analysis.
        analysis_name = gui_to_str(self.new_page.analysis_name.GetValue())

        # Go to the relax_disp.exp_type page.
        if analysis_name == 'Relaxation dispersion':
            return 1

        # Otherwise go to the pipe setup.
        else:
            return 2



class Data_pipe_page(Wiz_page):
    """The panel for setting the data pipe name."""

    # Class variables.
    image_path = WIZARD_IMAGE_PATH + 'pipe.png'
    main_text = u"Select the name of the data pipe used at the start of the analysis and the name of the data pipe bundle to be associated with this analysis.  All data in relax is kept within a special structure known as the relax data store.  This store is composed of multiple data pipes, each being associated with a specific analysis type.  Data pipe bundles are simple groupings of the pipes within the data store and each analysis tab is coupled to a specific bundle.\n\nSimple analyses such as the steady-state NOE and the R\u2081 and R\u2082 curve-fitting will be located within a single data pipe.  More complex analyses such as the automated model-free analysis will be spread across multiple data pipes, internally created by forking the original data pipe which holds the input data, all grouped together within a single bundle.\n\nThe initialisation of a new analysis will call the pipe.create user function with the pipe name and pipe bundle as given below."
    title = 'Data pipe set up'

    def add_contents(self, sizer):
        """Add the specific GUI elements (dummy method).

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The pipe name input.
        self.pipe_name = Value(name='pipe_name', parent=self, value_type='str', sizer=sizer, desc="The starting data pipe for the analysis:", divider=self._div_left, height_element=self.height_element)

        # The pipe bundle input.
        self.pipe_bundle = Value(name='pipe_bundle', parent=self, value_type='str', sizer=sizer, desc="The data pipe bundle:", divider=self._div_left, height_element=self.height_element)

        # Spacing.
        sizer.AddStretchSpacer(3)


    def on_display(self):
        """Update the pipe name."""

        # Generate a name for the data pipe bundle based on the type and time.
        name = "%s (%s)" % (self.parent.analysis_type, asctime(localtime()))

        # Update the fields.
        self.pipe_name.SetValue(str_to_gui("origin - %s" % name))
        self.pipe_bundle.SetValue(str_to_gui(name))



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
    image_path = IMAGE_PATH + "relax.gif"
    main_text = u"A number of automatic analyses to be preformed using relax in GUI mode.  Although not as flexible or powerful as the prompt/scripting modes, this provides a quick and easy setup and execution for a number of analysis types.   These currently include the calculation of the steady-state NOE, the exponential curve-fitting for the R\u2081 and R\u2082 relaxation rates, and for a full and automatic model-free analysis using the d'Auvergne and Gooley, 2008b protocol.  All analyses perform error propagation using the gold standard Monte Calro simulations.  Please select from one of the following analysis types:"
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
        self.image = wx.StaticBitmap(self, -1, bitmap_setup(self.image_path))
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
                           'mf': wx.NewId(),
                           'relax_disp': wx.NewId(),
                           'consist_test': wx.NewId(),
                           'custom': wx.NewId(),
                           'reserved': wx.NewId()}

        # The NOE button.
        self.button_noe = self.create_button(id=self.button_ids['noe'], box=sizer1, size=size, bmp=ANALYSIS_IMAGE_PATH+"noe_150x150.png", tooltip="Steady-state NOE analysis", fn=self.select_noe)

        # The R1 button.
        self.button_r1 = self.create_button(id=self.button_ids['r1'], box=sizer1, size=size, bmp=ANALYSIS_IMAGE_PATH+"r1_150x150.png", tooltip=u"R\u2081 relaxation curve-fitting analysis", fn=self.select_r1)

        # The R2 button.
        self.button_r2 = self.create_button(id=self.button_ids['r2'], box=sizer1, size=size, bmp=ANALYSIS_IMAGE_PATH+"r2_150x150.png", tooltip=u"R\u2082 relaxation curve-fitting analysis", fn=self.select_r2)

        # The relaxation dispersion button.
        self.button_disp = self.create_button(id=self.button_ids['relax_disp'], box=sizer2, size=size, bmp=ANALYSIS_IMAGE_PATH+"relax_disp_150x150.png", tooltip="Relaxation dispersion analysis", fn=self.select_disp)

        # Consistency testing.
        self.button_consist_test = self.create_button(id=self.button_ids['consist_test'], box=sizer2, size=size, bmp=ANALYSIS_IMAGE_PATH+"consistency_testing_150x70.png", tooltip="Relaxation data consistency testing (disabled)", fn=self.select_consist_test, disabled=True)

        # The model-free button.
        self.button_mf = self.create_button(id=self.button_ids['mf'], box=sizer2, size=size, bmp=ANALYSIS_IMAGE_PATH+"model_free"+sep+"model_free_150x150.png", tooltip="Model-free analysis", fn=self.select_mf)

        # The custom analysis button.
        self.button_custom = self.create_button(id=self.button_ids['custom'], box=sizer2, size=size, bmp=ANALYSIS_IMAGE_PATH+"custom_150x150.png", tooltip="Custom analysis (disabled)", fn=self.select_custom, disabled=True)

        # The blank reserved button.
        self.button_reserved = self.create_button(id=self.button_ids['reserved'], box=sizer2, size=size, bmp=ANALYSIS_IMAGE_PATH+"blank_150x150.png", tooltip=None, fn=None, disabled=True)

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
        self.analysis_name = Value(name='analysis_name', parent=self, value_type='str', sizer=sizer, desc="The name of the new analysis:", tooltip='The name of the analysis can be changed to any text.', divider=self._div_left, height_element=self.height_element)


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
        @type tooltip:      str or None
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
        if tooltip != None:
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


    def select_disp(self, event):
        """Relaxation dispersion analysis selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Toggle all buttons off.
        self.toggle(self.button_disp)

        # Update the analysis name.
        self.analysis_name.SetValue(str_to_gui('Relaxation dispersion'))

        # Set the analysis type.
        self.parent.analysis_type = 'relax_disp'


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
        self.analysis_name.SetValue(str_to_gui("R1 relaxation"))

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
        self.analysis_name.SetValue(str_to_gui("R2 relaxation"))

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
        self.button_mf.SetValue(False)
        self.button_disp.SetValue(False)
        self.button_consist_test.SetValue(False)
        self.button_custom.SetValue(False)
        self.button_reserved.SetValue(False)

        # Turn on the selected button.
        button.SetValue(True)

        # Refresh the GUI element.
        self.Refresh()

        # Unfreeze.
        self.Thaw()

        # Unblock forwards movement.
        self.parent.block_next(not self._select_flag)
