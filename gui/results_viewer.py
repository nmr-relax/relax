###############################################################################
#                                                                             #
# Copyright (C) 2010 Michael Bieri                                            #
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
"""Module containing the base class for the results frame."""

# Python module imports.
from string import upper
import wx
from wx.lib import buttons

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.pipes import cdp_name, pipe_names
from status import Status; status = Status()

# relax GUI module imports.
from gui.fonts import font
from gui.icons import relax_icons
from gui.misc import add_border, gui_to_str, open_file, str_to_gui
from gui.paths import icon_22x22


class Results_viewer(wx.Frame):
    """The results viewer frame."""

    # Some class variables.
    border = 10
    size = (800, 400)

    def __init__(self, gui):
        """Build the results frame.

        @param gui:                 The main GUI class.
        @type gui:                  gui.relax_gui.Main instance
        """

        # Store the main class.
        self.gui = gui

        # Initialise the base frame.
        wx.Frame.__init__(self, parent=gui, style=wx.DEFAULT_FRAME_STYLE)

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # Set the window title, size, etc.
        self.SetTitle("Results viewer")
        self.SetSize(self.size)

        # Pack a sizer into the panel.
        box_main = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(box_main)

        # Build the central sizer, with borders.
        box_centre = add_border(box_main, border=self.border, packing=wx.VERTICAL)

        # Build the analysis selector.
        self.build_analysis_sel(box_centre)

        # Spacer.
        box_centre.AddSpacer(self.border)

        # Add the list box.
        self.list = self.add_list_box(box_centre, fn=None)

        # Spacer.
        box_centre.AddSpacer(self.border)

        # Add the open button.
        self.button_open = buttons.ThemedGenBitmapTextButton(self, -1, None, " Open")
        self.button_open.SetBitmapLabel(wx.Bitmap(icon_22x22.document_open, wx.BITMAP_TYPE_ANY))
        self.button_open.SetFont(font.normal)
        self.button_open.SetMinSize((103, 33))
        self.gui.Bind(wx.EVT_BUTTON, self.open_result_file, self.button_open)
        box_centre.Add(self.button_open, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 5)

        # Bind some events.
        self.Bind(wx.EVT_COMBOBOX, self.update_pipes, self.pipe_name)
        self.Bind(wx.EVT_CLOSE, self.handler_close)

        # Initialise observer name.
        self.name = 'results viewer'


    def Show(self, show=True):
        """Change the behaviour of showing the window to update the content.

        @keyword show:  A flag which is True shows the window.
        @type show:     bool
        """

        # Register a few methods in the observer objects.
        status.observers.pipe_alteration.register(self.name, self.update_window)
        status.observers.exec_lock.register(self.name, self.activate)

        # Update the window.
        self.update_window()

        # Show the window using the base class method.
        if status.show_gui:
            super(Results_viewer, self).Show(show)


    def activate(self):
        """Activate or deactivate certain elements in response to the execution lock."""

        # Flag for enabling or disabling the elements.
        enable = False
        if not status.exec_lock.locked():
            enable = True

        # The pipe selector.
        self.pipe_name.Enable(enable)

        # The open button.
        self.button_open.Enable(enable)


    def add_list_box(self, box, fn=None):
        """Add a results list box.

        @param box:     The box sizer to pack the box into.
        @type box:      wx.BoxSizer instance
        @keyword fn:    The function to bind double click events to.
        @type fn:       method
        @return:        The list box element.
        @rtype:         wx.ListBox element
        """

        # Initialise the list box.
        list = wx.ListBox(self, -1, choices=[])

        # Bind events.
        self.gui.Bind(wx.EVT_LISTBOX_DCLICK, fn, list)

        # Add to the sizer.
        box.Add(list, 1, wx.ALL|wx.EXPAND, 0)

        # Return the list box.
        return list


    def build_analysis_sel(self, box):
        """Create the analysis selection element.

        @param box: The horizontal box element to pack the elements into.
        @type box:  wx.BoxSizer instance
        """

        # Use a horizontal packing of elements.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The text.
        label = wx.StaticText(self, -1, "Analysis selection")

        # The font and label properties.
        label.SetFont(font.subtitle)

        # Add the label to the analysis box.
        sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Add a spacer.
        sizer.AddSpacer(self.border)

        # A combo box.
        self.pipe_name = wx.ComboBox(self, -1, value='', style=wx.CB_DROPDOWN|wx.CB_READONLY, choices=[])
        self.pipe_name.SetMinSize((50, 27))
        sizer.Add(self.pipe_name, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Add the analysis sizer to the main sizer.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Unregister the methods from the observers to avoid unnecessary updating.
        status.observers.pipe_alteration.unregister(self.name)
        status.observers.exec_lock.unregister(self.name)

        # Close the window.
        self.Hide()


    def on_choice(self, event):
        """Update the list of results on choosing a data pipe.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the list.
        self.list.Clear()

        # Nothing to do.
        if not hasattr(cdp, 'result_files'):
            return

        # Update the list.
        for i in range(len(cdp.result_files)):
            # The text to display.
            text = "%s%s file:  %s" % (upper(cdp.result_files[i][0][0]), cdp.result_files[i][0][1:], cdp.result_files[i][1])

            # Add the text with the Python data.
            self.list.Append(str_to_gui(text), clientData=cdp.result_files[i])


    def open_result_file(self, event):
        """Open the results in the appropriate program.

        @param event:   The wx event.
        @type event:    wx event
        """

        # No choice.
        if self.list.GetSelection() == wx.NOT_FOUND:
            return

        # Get the data.
        data = self.list.GetClientData(self.list.GetSelection())

        # Grace files.
        if data[0] == 'grace':
            self.gui.user_functions.grace.view(None, file=data[1])

        # A special table.
        elif data[0] == 'Table_of_Results':
            # The data.
            model_result = [ds.relax_gui.table_residue, ds.relax_gui.table_model, ds.relax_gui.table_s2, ds.relax_gui.table_rex, ds.relax_gui.table_te]

        # Open all other files in which ever editor the platform decides on.
        else:
            open_file(data[1])


    def update_pipes(self, event):
        """Update the list of analyses.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Init.
        pipe_switch = False

        # The selected pipe.
        if event:
            # The name of the selected pipe.
            pipe = gui_to_str(event.GetString())

            # A pipe change.
            if pipe != cdp_name():
                pipe_switch = True
        else:
            pipe = cdp_name()
        if not pipe:
            pipe = ''

        # Clear the previous analyses.
        self.pipe_name.Clear()

        # The list of analyses.
        for pipe in pipe_names():
            self.pipe_name.Append(str_to_gui(pipe))

        # Switch.
        if pipe_switch:
            # Switch data pipes.
            self.gui.interpreter.pipe.switch(pipe)

            # Update the tree view.
            self.on_choice(None)

        # Set the name to the current data pipe.
        self.pipe_name.SetValue(str_to_gui(pipe))


    def update_window(self, event=None):
        """Update the window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Update the choices.
        self.update_pipes(None)

        # Update the list.
        self.on_choice(None)
