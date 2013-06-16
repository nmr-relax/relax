###############################################################################
#                                                                             #
# Copyright (C) 2010-2013 Edward d'Auvergne                                   #
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
"""The spin viewer frame."""

# Python module imports.
import wx

# relax module imports.
from graphics import WIZARD_IMAGE_PATH, fetch_icon
from gui.icons import relax_icons
from gui.misc import gui_raise
from gui.spin_viewer.splitter import Tree_splitter
from gui.string_conv import gui_to_str, str_to_gui
from gui.wizards.wiz_objects import Wiz_page, Wiz_window
from gui.uf_objects import build_uf_menus, Uf_storage; uf_store = Uf_storage()
from lib.errors import RelaxNoPipeError
from pipe_control.pipes import cdp_name, pipe_names
from status import Status; status = Status()


class Spin_view_window(wx.Frame):
    """A window element for the tree view."""

    def __init__(self, *args, **kwds):
        """Set up the relax prompt."""

        # Store the parent object.
        self.gui = kwds.pop('parent')

        # Create GUI elements
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        if not status.debug and status.wx_info["os"] != 'darwin':
            kwds["style"] = kwds["style"] | wx.MAXIMIZE
        wx.Frame.__init__(self, *args, **kwds)

        # Force the main window to start maximised (needed for MS Windows).
        if not status.debug and status.wx_info["os"] != 'darwin':
            self.Maximize()

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # Some default values.
        self.size_x = 1000
        self.size_y = 750

        # Set up the window.
        sizer = self.setup_window()

        # Create a menu.
        self._create_menu()

        # Build the toolbar.
        self.toolbar()

        # The splitter window.
        splitter = Tree_splitter(self.gui, self, -1)
        sizer.Add(splitter, 1, wx.EXPAND|wx.ALL, 0)

        # Initialise observer name.
        self.name = 'spin viewer'


    def _activate(self):
        """Activate or deactivate certain elements in response to the execution lock."""

        # Flag for enabling or disabling the elements.
        enable = False
        if not status.exec_lock.locked():
            enable = True

        # Loop over the menus.
        for menu, label in self.menubar.GetMenus():
            # Loop over the menu items.
            for item in menu.GetMenuItems():
                wx.CallAfter(item.Enable, enable)

        # The spin loader.
        wx.CallAfter(self.bar.EnableTool, self.spin_loader_id, enable)

        # The pipe selector.
        wx.CallAfter(self.pipe_name.Enable, enable)


    def _create_menu(self):
        """Build a menu for the window."""

        # Create the menu bar GUI item and add it to the main frame.
        self.menubar = wx.MenuBar()
        if status.show_gui:
            self.SetMenuBar(self.menubar)

        # The user function menus.
        self.menu_uf_ids = build_uf_menus(parent=self, menubar=self.menubar)


    def Show(self, show=True):
        """Change the behaviour of showing the window to update the content.

        @keyword show:  A flag which is True shows the window.
        @type show:     bool
        """

        # Register a few methods in the observer objects.
        status.observers.gui_uf.register(self.name, self.refresh, method_name='ref')
        status.observers.pipe_alteration.register(self.name, self.refresh, method_name='ref')
        status.observers.exec_lock.register(self.name, self._activate, method_name='_activate')

        # First update.
        self.refresh()

        # Activate or deactivate the frame.
        self._activate()

        # Then show the window using the base class method.
        if status.show_gui:
            super(Spin_view_window, self).Show(show)


    def refresh(self, event=None):
        """Event handler for the refresh action (thread safe).

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Thread safe.
        wx.CallAfter(self.refresh_safe)


    def refresh_safe(self):
        """Refresh the spin viewer window."""

        # Change the cursor to busy.
        wx.BeginBusyCursor()

        # Update the data pipe selector.
        self.update_pipes()

        # Update the tree.
        self.tree_panel.update()

        # Redisplay the container.
        self.container.display(self.tree_panel.get_info())

        # Reset the cursor.
        if wx.IsBusy():
            wx.EndBusyCursor()


    def handler_close(self, event=None):
        """Event handler for the close window action.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Unregister the methods from the observers to avoid unnecessary updating.
        status.observers.gui_uf.unregister(self.name)
        status.observers.pipe_alteration.unregister(self.name)
        status.observers.exec_lock.unregister(self.name)

        # Close the window.
        self.Hide()


    def load_spins_wizard(self, event=None):
        """The spin loading wizard.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # No current data pipe.
        if not cdp_name():
            gui_raise(RelaxNoPipeError())
            return

        # Change the cursor to busy.
        wx.BeginBusyCursor()

        # Initialise a wizard.
        self.wizard = Wiz_window(parent=self, size_x=1000, size_y=800, title="Load spins")
        self.page_indices = {}

        # The loading method page.
        self.page_method = Load_method_page(self.wizard)
        self.page_indices['method'] = self.wizard.add_page(self.page_method, apply_button=True, skip_button=False)
        self.wizard.set_seq_next_fn(self.page_indices['method'], self.wizard_page_after_load_method)

        # The sequence.read page.
        page = uf_store['sequence.read'].create_page(self.wizard)
        self.page_indices['sequence.read'] = self.wizard.add_page(page, skip_button=True)
        self.wizard.set_seq_next_fn(self.page_indices['sequence.read'], self.wizard_page_after_sequence_read)

        # The structure.read_pdb page.
        page = uf_store['structure.read_pdb'].create_page(self.wizard)
        self.page_indices['structure.read_pdb'] = self.wizard.add_page(page, skip_button=True)
        self.wizard.set_seq_next_fn(self.page_indices['structure.read_pdb'], self.wizard_page_after_structure_read)

        # The structure.read_xyz page.
        page = uf_store['structure.read_xyz'].create_page(self.wizard)
        self.page_indices['structure.read_xyz'] = self.wizard.add_page(page, skip_button=True)
        self.wizard.set_seq_next_fn(self.page_indices['structure.read_xyz'], self.wizard_page_after_structure_read)

        # The structure.load_spins page.
        page = uf_store['structure.load_spins'].create_page(self.wizard)
        self.page_indices['structure.load_spins'] = self.wizard.add_page(page)

        # The termination page.
        page = Finish_page(self.wizard)
        self.page_indices['fin'] = self.wizard.add_page(page, apply_button=False, skip_button=False)

        # Reset the cursor.
        if wx.IsBusy():
            wx.EndBusyCursor()

        # Run the wizard.
        self.wizard.run()


    def setup_window(self):
        """Set up the window.

        @return:    The sizer object.
        @rtype:     wx.Sizer instance
        """

        # Set the frame title.
        self.SetTitle("The spin viewer")

        # Use a box sizer for packing the shell.
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Close the window cleanly (hide so it can be reopened).
        self.Bind(wx.EVT_CLOSE, self.handler_close)

        # Set the default size of the controller.
        self.SetSize((self.size_x, self.size_y))

        # Return the sizer.
        return sizer


    def toolbar(self):
        """Create the toolbar."""

        # Init.
        self.bar = self.CreateToolBar(wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_TEXT)

        # The spin loading button.
        self.spin_loader_id = wx.NewId()
        tooltip = "Load spins from either a sequence file or from a 3D structure file."
        self.bar.AddLabelTool(self.spin_loader_id, "Load spins", wx.Bitmap(fetch_icon('relax.spin', '32x32'), wx.BITMAP_TYPE_ANY), bmpDisabled=wx.Bitmap(fetch_icon('relax.spin_grey', '32x32'), wx.BITMAP_TYPE_ANY), shortHelp=tooltip, longHelp=tooltip)
        self.Bind(wx.EVT_TOOL, self.load_spins_wizard, id=self.spin_loader_id)

        # A separator.
        self.bar.AddSeparator()

        # The refresh button.
        id = wx.NewId()
        tooltip = "Refresh the spin view."
        self.bar.AddLabelTool(id, "Refresh", wx.Bitmap(fetch_icon('oxygen.actions.view-refresh', '32x32'), wx.BITMAP_TYPE_ANY), shortHelp=tooltip, longHelp=tooltip)
        self.Bind(wx.EVT_TOOL, self.refresh, id=id)

        # A separator.
        self.bar.AddSeparator()

        # The pipe text.
        text = wx.StaticText(self.bar, -1, ' Current data pipe:  ', style=wx.ALIGN_LEFT)
        self.bar.AddControl(text)

        # The pipe selection.
        self.pipe_name = wx.ComboBox(self.bar, -1, "", style=wx.CB_DROPDOWN|wx.CB_READONLY, choices=[])
        self.bar.AddControl(self.pipe_name)
        self.Bind(wx.EVT_COMBOBOX, self.update_pipes, self.pipe_name)

        # Build the toolbar.
        self.bar.Realize()


    def uf_call(self, event=None):
        """Catch the user function call to properly specify the parent window.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # The user function ID.
        uf_id = event.GetId()

        # Get the user function name.
        name = uf_store.get_uf(uf_id)

        # Call the user function GUI object.
        uf_store[name](event=event, wx_parent=self)


    def update_pipes(self, event=None):
        """Update the spin view data pipe selector.

        @keyword event: The wx event.
        @type event:    wx event
        """

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

        # Switch.
        if pipe_switch:
            # Switch data pipes.
            self.gui.interpreter.apply('pipe.switch', pipe)

            # Update the tree view.
            self.tree_panel.update()

        # Set the pipe name to the cdp.
        self.pipe_name.SetValue(str_to_gui(pipe))

        # Reset the cursor.
        if wx.IsBusy():
            wx.EndBusyCursor()


    def wizard_page_after_load_method(self):
        """Set the page after the load method choice.

        @return:    The index of the next page.
        @rtype:     int
        """

        # Go to the sequence.read page.
        if self.page_method.selection == 'sequence':
            return self.page_indices['sequence.read']

        # Go to the structure.read_pdb page.
        elif self.page_method.selection == 'new pdb':
            return self.page_indices['structure.read_pdb']

        # Go to the structure.read_xyz page.
        elif self.page_method.selection == 'new xyz':
            return self.page_indices['structure.read_xyz']

        # Skip to the structure.load_spins page.
        elif self.page_method.selection == 'preload':
            return self.page_indices['structure.load_spins']


    def wizard_page_after_sequence_read(self):
        """Set the page after the sequence.read user function page.

        @return:    The index of the last page.
        @rtype:     int
        """

        # Return the index of the terminal page.
        return  self.page_indices['fin']


    def wizard_page_after_structure_read(self):
        """Set the page after the structure.read_* user function pages.

        @return:    The index of the structure.load_spins page.
        @rtype:     int
        """

        # Return the index of the terminal page.
        return  self.page_indices['structure.load_spins']



class Finish_page(Wiz_page):
    """The terminating wizard page."""

    # Class variables.
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    main_text = 'The spin systems should now have been loaded into the relax data store.'
    title = 'Spin loading complete'

    def add_contents(self, sizer):
        """This blank method is needed so that the page shows and does nothing.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """



class Load_method_page(Wiz_page):
    """The wizard page for specifying how to load spins."""

    # Class variables.
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    main_text = 'Select the method for loading spins into relax.  Two options are possible: the first is to read sequence information out of a text file via the sequence.read user function; the second is to read in a 3D structure file via the structure.read_pdb user function and then to load the spins from this structure using the structure.load_spins user function.'
    title = 'Spin loading'


    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Intro text.
        msg = "Please specify by which method spins should be loaded into the relax data store:"
        text = wx.StaticText(self, -1, msg)
        text.Wrap(self._main_size)
        sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # Spacing.
        sizer.AddStretchSpacer()

        # A box sizer for placing the box sizer in.
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer2, 1, wx.ALL|wx.EXPAND, 0)

        # Bottom spacing.
        sizer.AddStretchSpacer()

        # A bit of indentation.
        sizer2.AddStretchSpacer()

        # A vertical sizer for the radio buttons.
        sizer_radio = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(sizer_radio, 1, wx.ALL|wx.EXPAND, 0)

        # Pre-loaded structure exists.
        self.preload_flag = False
        if hasattr(cdp, 'structure') and not cdp.structure.empty():
            self.preload_flag = True

        # The pre-load radio button.
        if self.preload_flag:
            # The button.
            self.radio_preload = wx.RadioButton(self, -1, "From a pre-loaded structure.", style=wx.RB_GROUP)
            sizer_radio.Add(self.radio_preload, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

            # Spacing.
            sizer_radio.AddSpacer(20)

        # The sequence radio button.
        if self.preload_flag:
            style = 0
        else:
            style = wx.RB_GROUP
        self.radio_seq = wx.RadioButton(self, -1, "From a file containing sequence data.", style=style)
        sizer_radio.Add(self.radio_seq, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # Spacing.
        sizer_radio.AddSpacer(20)

        # The PDB radio button.
        self.radio_new_pdb = wx.RadioButton(self, -1, "From a new PDB structure file.")
        sizer_radio.Add(self.radio_new_pdb, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # Spacing.
        sizer_radio.AddSpacer(20)

        # The XYZ radio button.
        self.radio_new_xyz = wx.RadioButton(self, -1, "From a new XYZ structure file.")
        sizer_radio.Add(self.radio_new_xyz, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # Bind the buttons.
        self.Bind(wx.EVT_RADIOBUTTON, self._on_select, self.radio_seq)
        self.Bind(wx.EVT_RADIOBUTTON, self._on_select, self.radio_new_pdb)
        self.Bind(wx.EVT_RADIOBUTTON, self._on_select, self.radio_new_xyz)
        if self.preload_flag:
            self.Bind(wx.EVT_RADIOBUTTON, self._on_select, self.radio_preload)

        # Right side spacing.
        sizer2.AddStretchSpacer(3)

        # Bottom spacing.
        sizer.AddStretchSpacer()

        # Set the default selection.
        if self.preload_flag:
            self.selection = 'preload'
        else:
            self.selection = 'sequence'


    def _on_select(self, event=None):
        """Handle the radio button switching.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # The button.
        button = event.GetEventObject()

        # RMSD.
        if button == self.radio_seq:
            self.selection = 'sequence'
        elif button == self.radio_new_pdb:
            self.selection = 'new pdb'
        elif button == self.radio_new_xyz:
            self.selection = 'new xyz'
        elif self.preload_flag and button == self.radio_preload:
            self.selection = 'preload'
