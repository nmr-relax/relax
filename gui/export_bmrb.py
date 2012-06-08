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
"""The BMRB export wizard."""

# Python module imports.
import wx

# relax module imports.
from generic_fns.pipes import cdp_name, pipe_names, switch
from graphics import IMAGE_PATH, fetch_icon
from status import Status; status = Status()

# relax GUI module imports.
from gui.components.citations import Citations
from gui.components.molecule import Molecule
from gui.components.relax_data_meta import Relax_data_meta_list
from gui.components.scripts import Scripts
from gui.components.software import Software
from gui.fonts import font
from gui.icons import relax_icons
from gui.input_elements.value import Value
from gui.misc import add_border
from gui.string_conv import gui_to_str, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()


class Export_bmrb_window(wx.Frame):
    """The BMRB export window."""

    def __init__(self, gui):
        """Set up the export window.

        @param gui:     The GUI object.
        @type gui:      wx.Frame instance
        """

        # The window style.
        style = wx.DEFAULT_FRAME_STYLE
        if not status.debug and status.wx_info["os"] != 'darwin':
            style = style | wx.MAXIMIZE

        # Initialise the base class, setting the main GUI window as the parent.
        super(Export_bmrb_window, self).__init__(gui, -1, style=style)

        # Some default values.
        self.size = (1200, 900)
        self.size_min = (900, 700)
        self.border = 5
        self.spacer = 10
        self.button_size = (200, 40)
        self.button_spacing = 10
        self.main_spacing = 20

        # Set up the frame.
        sizer = self.setup_frame()

        # Add the header.
        self.add_header(sizer)

        # Top spacing.
        sizer.AddSpacer(10)

        # Add the data pipe selection element.
        self.add_pipe(sizer)

        # Spacing.
        sizer.AddSpacer(self.main_spacing)

        # Add the relaxation data metadata list GUI element.
        self.relax_data = Relax_data_meta_list(parent=self.main_panel, box=sizer, id='BMRB export', stretch=True)

        # Spacing.
        sizer.AddSpacer(self.main_spacing)

        # Add the molecule GUI element.
        self.molecule = Molecule(parent=self.main_panel, box=sizer, id='BMRB export', stretch=True)

        # Spacing.
        sizer.AddSpacer(self.main_spacing)

        # Create a horizontal layout for the software, script and citations GUI elements.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add the software GUI element.
        self.software = Software(parent=self.main_panel, box=sub_sizer, id='BMRB export', stretch=True)

        # Vertical spacing.
        sub_sizer.AddSpacer(self.main_spacing)

        # Add the scripts GUI element.
        self.scripts = Scripts(parent=self.main_panel, box=sub_sizer, id='BMRB export', stretch=True)

        # Vertical spacing.
        sub_sizer.AddSpacer(self.main_spacing)

        # Add the citation GUI element.
        self.citation = Citations(parent=self.main_panel, box=sub_sizer, id='BMRB export', stretch=True)

        # Add the sizer.
        sizer.Add(sub_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Bottom spacing.
        sizer.AddSpacer(5)

        # Add the buttons.
        self.add_buttons(sizer)

        # Open the window.
        if status.show_gui:
            self.Show()


    def action_cancel(self, event=None):
        """Cancel the export.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Close the window.
        self.Close()


    def action_export(self, event=None):
        """Write out the NMR-STAR formatted data.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Execute the user function.
        uf_store['bmrb.write'](wx_parent=self, wx_wizard_sync=True, wx_wizard_modal=True)

        # Close the window.
        self.Close()


    def action_preview(self, event=None):
        """Preview the NMR-STAR formatted data.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Execute the user function.
        uf_store['bmrb.display'](wx_parent=self)


    def add_buttons(self, sizer):
        """Build and add the bottom buttons.

        @param sizer:   The sizer element to pack the buttons into.
        @type sizer:    wx.Sizer instance
        """

        # Button sizer.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT, 0)

        # Preview button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self.main_panel, -1, None, " Preview")
        button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.document-preview', "32x32"), wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetMinSize(self.button_size)
        button_sizer.Add(button, 0, 0, 0)
        self.Bind(wx.EVT_BUTTON, self.action_preview, button)
        button.SetToolTipString("Preview the NMR-STAR formatted data.")

        # Spacing.
        button_sizer.AddSpacer(self.button_spacing)

        # Export button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self.main_panel, -1, None, " Export")
        button.SetBitmapLabel(wx.Bitmap(fetch_icon('relax.bmrb', "32x32"), wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetMinSize(self.button_size)
        button_sizer.Add(button, 0, 0, 0)
        self.Bind(wx.EVT_BUTTON, self.action_export, button)
        button.SetToolTipString("Preview the NMR-STAR formatted data.")

        # Spacing.
        button_sizer.AddSpacer(self.button_spacing)

        # Cancel button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self.main_panel, -1, None, " Cancel")
        button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.dialog-cancel', "32x32"), wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetMinSize(self.button_size)
        button_sizer.Add(button, 0, 0, 0)
        self.Bind(wx.EVT_BUTTON, self.action_cancel, button)
        button.SetToolTipString("Cancel the BMRB export.")


    def add_header(self, sizer):
        """Build and add the header to the sizer.

        @param sizer:   The sizer element to pack the header into.
        @type sizer:    wx.Sizer instance
        """

        # Create a horizontal layout.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left spacing.
        sub_sizer.AddStretchSpacer(3)

        # Add the BMRB logo (left side).
        logo = wx.StaticBitmap(self.main_panel, -1, wx.Bitmap(IMAGE_PATH+"bmrb_100x100.png", wx.BITMAP_TYPE_ANY))
        sub_sizer.Add(logo, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Spacing.
        sub_sizer.AddStretchSpacer()

        # The text sizer.
        text_sizer = wx.BoxSizer(wx.VERTICAL)

        # The title.
        text = wx.StaticText(self.main_panel, -1, 'Data export for BMRB deposition', style=wx.ALIGN_LEFT)
        text.SetFont(font.title)
        text_sizer.Add(text, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Spacing.
        text_sizer.AddSpacer(15)

        # The text.
        main_text = 'This wizard will help in executing all of the relevant user functions required to convert the contents of the selected data pipe to the NMR-STAR format for deposition within the BioMagResBank.  Note that this is currently only for the deposition of model-free analysis results or simple NMR relaxation data.'
        text = wx.StaticText(self.main_panel, -1, main_text, style=wx.ALIGN_LEFT)
        text.Wrap(600)
        text.SetFont(font.normal)
        text_sizer.Add(text, 0, 0, 0)

        # Add the text sizer.
        sub_sizer.Add(text_sizer, 0, 0, 0)

        # Spacing.
        sub_sizer.AddStretchSpacer()

        # Add the BMRB logo (right side).
        logo = wx.StaticBitmap(self.main_panel, -1, wx.Bitmap(IMAGE_PATH+"bmrb_100x100.png", wx.BITMAP_TYPE_ANY))
        sub_sizer.Add(logo, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Right spacing.
        sub_sizer.AddStretchSpacer(3)

        # Add the sizer.
        sizer.Add(sub_sizer, 0, wx.ALL|wx.EXPAND, 0)

        # A line with spacing.
        sizer.AddSpacer(10)
        sizer.Add(wx.StaticLine(self.main_panel, -1), 0, wx.EXPAND|wx.ALL, 0)
        sizer.AddSpacer(10)


    def add_pipe(self, sizer):
        """Build and add the data pipe selection element.

        @param sizer:   The sizer element to pack the buttons into.
        @type sizer:    wx.Sizer instance
        """

        # A sizer for the element.
        pipe_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(pipe_sizer, 0, wx.ALIGN_LEFT, 0)

        # The pipe text.
        text = wx.StaticText(self.main_panel, -1, ' The data pipe to export:  ', style=wx.ALIGN_LEFT)
        tooltip = "The name of the data pipe to export to NMR-STAR format for BMRB export."
        text.SetFont(font.normal)
        text.SetToolTipString(tooltip)
        pipe_sizer.Add(text, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        # Spacing.
        pipe_sizer.AddSpacer(20)

        # The pipe selection.
        self.pipe_name = wx.ComboBox(self.main_panel, -1, "", style=wx.CB_DROPDOWN|wx.CB_READONLY, choices=[])
        self.pipe_name.SetToolTipString(tooltip)
        self.Bind(wx.EVT_COMBOBOX, self.update_pipes, self.pipe_name)
        pipe_sizer.Add(self.pipe_name, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        # Update the pipe selection.
        self.update_pipes()


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Unregister the observers.
        self.observer_register(remove=True)

        # Close the window.
        event.Skip()


    def observer_register(self, remove=False):
        """Register and unregister methods with the observer objects.

        @keyword remove:    If set to True, then the methods will be unregistered.
        @type remove:       False
        """

        # Register.
        if not remove:
            status.observers.pipe_alteration.register('BMRB export', self.update_pipes)

        # Unregister.
        else:
            # The class methods.
            status.observers.pipe_alteration.unregister('BMRB export')

            # The embedded objects methods.
            self.relax_data.observer_register(remove=True)
            self.molecule.observer_register(remove=True)
            self.software.observer_register(remove=True)
            self.scripts.observer_register(remove=True)
            self.citation.observer_register(remove=True)


    def setup_frame(self):
        """Set up the relax controller frame.
        @return:    The sizer object.
        @rtype:     wx.Sizer instance
        """

        # Set the frame title.
        self.SetTitle("BMRB export window")

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # Place all elements within a panel (to remove the dark grey in MS Windows).
        self.main_panel = wx.Panel(self, -1)

        # Use a grid sizer for packing the main elements.
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel.SetSizer(main_sizer)

        # Build the central sizer, with borders.
        sizer = add_border(main_sizer, border=self.border, packing=wx.VERTICAL)

        # Close the window cleanly (unregistering observers).
        self.Bind(wx.EVT_CLOSE, self.handler_close)

        # Set the default size of the controller.
        self.SetSize(self.size)
        self.SetMinSize(self.size_min)

        # Centre the frame.
        self.Centre()

        # Return the central sizer.
        return sizer


    def update_pipes(self, event=None):
        """Update the spin view data pipe selector.

        @keyword event: The wx event.
        @type event:    wx event
        """

        print "update pipes!"

        # Change the cursor to busy.
        wx.BeginBusyCursor()

        # Init.
        pipe_switch = False

        # The selected pipe.
        if event:
            # The name of the selected pipe.
            pipe = gui_to_str(self.pipe_name.GetString(event.GetSelection()))

            # A pipe change.
            if pipe != cdp_name():
                pipe_switch = True
        else:
            pipe = cdp_name()
        if not pipe:
            pipe = ''

        # Clear the previous data.
        self.pipe_name.Clear()

        # The list of pipe names.
        for name in pipe_names():
            self.pipe_name.Append(str_to_gui(name))

        # Switch data pipes.
        if pipe_switch:
            switch(pipe)

        # Set the pipe name to the cdp.
        self.pipe_name.SetValue(str_to_gui(pipe))

        # Reset the cursor.
        if wx.IsBusy():
            wx.EndBusyCursor()
