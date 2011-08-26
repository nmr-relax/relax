###############################################################################
#                                                                             #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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
"""The spin viewer frame."""


# Python module imports.
import wx

# relax module imports.
from generic_fns.pipes import cdp_name, pipe_names
from status import Status; status = Status()

# relax GUI module imports.
from gui import paths
from gui.components.menu import build_menu_item
from gui.icons import relax_icons
from gui.misc import gui_to_str, str_to_gui
from gui.spin_viewer.splitter import Tree_splitter


class Spin_view_window(wx.Frame):
    """A window element for the tree view."""

    # Some IDs for the menu entries.
    MENU_SEQUENCE_COPY = wx.NewId()
    MENU_SEQUENCE_READ = wx.NewId()
    MENU_SEQUENCE_WRITE = wx.NewId()
    MENU_STRUCTURE_DELETE = wx.NewId()
    MENU_STRUCTURE_LOAD_SPINS = wx.NewId()
    MENU_STRUCTURE_READ_PDB = wx.NewId()
    MENU_STRUCTURE_WRITE_PDB = wx.NewId()
    MENU_MOLECULE_COPY = wx.NewId()
    MENU_MOLECULE_CREATE = wx.NewId()
    MENU_MOLECULE_DELETE = wx.NewId()
    MENU_RESIDUE_COPY = wx.NewId()
    MENU_RESIDUE_CREATE = wx.NewId()
    MENU_RESIDUE_DELETE = wx.NewId()
    MENU_SPIN_COPY = wx.NewId()
    MENU_SPIN_CREATE = wx.NewId()
    MENU_SPIN_CREATE_PSEUDO = wx.NewId()
    MENU_SPIN_DELETE = wx.NewId()
    MENU_SPIN_DISPLAY = wx.NewId()
    MENU_SPIN_ELEMENT = wx.NewId()
    MENU_SPIN_NAME = wx.NewId()
    MENU_SPIN_NUMBER = wx.NewId()
    MENU_SELECT_ALL = wx.NewId()
    MENU_SELECT_READ = wx.NewId()
    MENU_SELECT_REVERSE = wx.NewId()
    MENU_SELECT_SPIN = wx.NewId()
    MENU_DESELECT_ALL = wx.NewId()
    MENU_DESELECT_READ = wx.NewId()
    MENU_DESELECT_REVERSE = wx.NewId()
    MENU_DESELECT_SPIN = wx.NewId()

    def __init__(self, *args, **kwds):
        """Set up the relax prompt."""

        # Store the parent object.
        self.gui = kwds.pop('parent')

        # Create GUI elements
        kwds["style"] = wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE
        wx.Frame.__init__(self, *args, **kwds)

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

        # The menu bar.
        self.menubar.Enable(self.MENU_SEQUENCE_COPY, enable)
        self.menubar.Enable(self.MENU_SEQUENCE_READ, enable)
        self.menubar.Enable(self.MENU_SEQUENCE_WRITE, enable)
        self.menubar.Enable(self.MENU_STRUCTURE_DELETE, enable)
        self.menubar.Enable(self.MENU_STRUCTURE_LOAD_SPINS, enable)
        self.menubar.Enable(self.MENU_STRUCTURE_READ_PDB, enable)
        self.menubar.Enable(self.MENU_STRUCTURE_WRITE_PDB, enable)
        self.menubar.Enable(self.MENU_MOLECULE_COPY, enable)
        self.menubar.Enable(self.MENU_MOLECULE_CREATE, enable)
        self.menubar.Enable(self.MENU_MOLECULE_DELETE, enable)
        self.menubar.Enable(self.MENU_RESIDUE_COPY, enable)
        self.menubar.Enable(self.MENU_RESIDUE_CREATE, enable)
        self.menubar.Enable(self.MENU_RESIDUE_DELETE, enable)
        self.menubar.Enable(self.MENU_SPIN_COPY, enable)
        self.menubar.Enable(self.MENU_SPIN_CREATE, enable)
        self.menubar.Enable(self.MENU_SPIN_CREATE_PSEUDO, enable)
        self.menubar.Enable(self.MENU_SPIN_DELETE, enable)
        self.menubar.Enable(self.MENU_SPIN_DISPLAY, enable)
        self.menubar.Enable(self.MENU_SPIN_ELEMENT, enable)
        self.menubar.Enable(self.MENU_SPIN_NAME, enable)
        self.menubar.Enable(self.MENU_SPIN_NUMBER, enable)
        self.menubar.Enable(self.MENU_SELECT_ALL, enable)
        self.menubar.Enable(self.MENU_SELECT_READ, enable)
        self.menubar.Enable(self.MENU_SELECT_REVERSE, enable)
        self.menubar.Enable(self.MENU_SELECT_SPIN, enable)
        self.menubar.Enable(self.MENU_DESELECT_ALL, enable)
        self.menubar.Enable(self.MENU_DESELECT_READ, enable)
        self.menubar.Enable(self.MENU_DESELECT_REVERSE, enable)
        self.menubar.Enable(self.MENU_DESELECT_SPIN, enable)

        # The pipe selector.
        self.pipe_name.Enable(enable)


    def _create_menu(self):
        """Build a menu for the window."""

        # Create the menu bar GUI item and add it to the main frame.
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)

        # The sequence menu entry.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SEQUENCE_COPY, text="&copy", icon=paths.icon_16x16.copy, fn=self.gui.user_functions.sequence.copy))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SEQUENCE_READ, text="&read", icon=paths.icon_16x16.open, fn=self.gui.user_functions.sequence.read))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SEQUENCE_WRITE, text="&write", icon=paths.icon_16x16.save, fn=self.gui.user_functions.sequence.write))
        self.menubar.Append(menu, "se&quence")

        # The structure menu entry.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_STRUCTURE_DELETE, text="&delete", icon=paths.icon_16x16.remove, fn=self.gui.user_functions.structure.delete))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_STRUCTURE_LOAD_SPINS, text="&load_spins", icon=paths.icon_16x16.spin, fn=self.gui.user_functions.structure.load_spins))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_STRUCTURE_READ_PDB, text="&read_pdb", icon=paths.icon_16x16.open, fn=self.gui.user_functions.structure.read_pdb))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_STRUCTURE_WRITE_PDB, text="&write_pdb", icon=paths.icon_16x16.save, fn=self.gui.user_functions.structure.write_pdb))
        self.menubar.Append(menu, "st&ructure")

        # The molecule menu entry.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_MOLECULE_COPY, text="&copy", icon=paths.icon_16x16.copy, fn=self.gui.user_functions.molecule.copy))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_MOLECULE_CREATE, text="crea&te", icon=paths.icon_16x16.add, fn=self.gui.user_functions.molecule.create))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_MOLECULE_DELETE, text="&delete", icon=paths.icon_16x16.remove, fn=self.gui.user_functions.molecule.delete))
        self.menubar.Append(menu, "&molecule")

        # The residue menu entry.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_RESIDUE_COPY, text="&copy", icon=paths.icon_16x16.copy, fn=self.gui.user_functions.residue.copy))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_RESIDUE_CREATE, text="crea&te", icon=paths.icon_16x16.add, fn=self.gui.user_functions.residue.create))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_RESIDUE_DELETE, text="&delete", icon=paths.icon_16x16.remove, fn=self.gui.user_functions.residue.delete))
        self.menubar.Append(menu, "&residue")

        # The spin menu entry.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SPIN_COPY, text="&copy", icon=paths.icon_16x16.copy, fn=self.gui.user_functions.spin.copy))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SPIN_CREATE, text="crea&te", icon=paths.icon_16x16.add, fn=self.gui.user_functions.spin.create))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SPIN_CREATE_PSEUDO, text="create_&pseudo", icon=paths.icon_16x16.add, fn=self.gui.user_functions.spin.create_pseudo))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SPIN_DELETE, text="&delete", icon=paths.icon_16x16.remove, fn=self.gui.user_functions.spin.delete))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SPIN_DISPLAY, text="displa&y", icon=None, fn=self.gui.user_functions.spin.display))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SPIN_ELEMENT, text="&element", icon=None, fn=self.gui.user_functions.spin.element))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SPIN_NAME, text="&name", icon=None, fn=self.gui.user_functions.spin.name))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SPIN_NUMBER, text="num&ber", icon=None, fn=self.gui.user_functions.spin.number))
        self.menubar.Append(menu, "&spin")

        # The select menu entry.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SELECT_ALL, text="&all", icon=None, fn=self.gui.user_functions.select.all))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SELECT_READ, text="&read", icon=paths.icon_16x16.open, fn=self.gui.user_functions.select.read))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SELECT_REVERSE, text="re&verse", icon=None, fn=self.gui.user_functions.select.reverse))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_SELECT_SPIN, text="&spin", icon=paths.icon_16x16.spin, fn=self.gui.user_functions.select.spin))
        self.menubar.Append(menu, "se&lect")

        # The deselect menu entry.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_DESELECT_ALL, text="&all", icon=None, fn=self.gui.user_functions.deselect.all))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_DESELECT_READ, text="&read", icon=paths.icon_16x16.open, fn=self.gui.user_functions.deselect.read))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_DESELECT_REVERSE, text="re&verse", icon=None, fn=self.gui.user_functions.deselect.reverse))
        menu.AppendItem(build_menu_item(menu, parent=self, id=self.MENU_DESELECT_SPIN, text="&spin", icon=paths.icon_16x16.spin, fn=self.gui.user_functions.deselect.spin))
        self.menubar.Append(menu, "&deselect")


    def Show(self, show=True):
        """Change the behaviour of showing the window to update the content.

        @keyword show:  A flag which is True shows the window.
        @type show:     bool
        """

        # Register a few methods in the observer objects.
        status.observers.gui_uf.register(self.name, self.refresh)
        status.observers.pipe_alteration.register(self.name, self.refresh)
        status.observers.exec_lock.register(self.name, self._activate)

        # First update.
        self.refresh()

        # Activate or deactivate the frame.
        self._activate()

        # Then show the window using the base class method.
        if status.show_gui:
            super(Spin_view_window, self).Show(show)


    def refresh(self, event=None):
        """Event handler for the refresh action (thread safe).

        @param event:   The wx event.
        @type event:    wx event
        """

        # Thread safe.
        wx.CallAfter(self.refresh_safe)

        # Flush the events.
        wx.Yield()


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
        wx.EndBusyCursor()


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Unregister the methods from the observers to avoid unnecessary updating.
        status.observers.gui_uf.unregister(self.name)
        status.observers.pipe_alteration.unregister(self.name)
        status.observers.exec_lock.unregister(self.name)

        # Close the window.
        self.Hide()


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
        self.bar = self.CreateToolBar(wx.TB_HORIZONTAL|wx.TB_FLAT)

        # The refresh button.
        id = wx.NewId()
        self.bar.AddLabelTool(id, "Refresh", wx.Bitmap(paths.icon_32x32.view_refresh, wx.BITMAP_TYPE_ANY), shortHelp="Refresh", longHelp="Refresh the spin view")
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


    def update_pipes(self, event=None):
        """Update the spin view data pipe selector.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Change the cursor to busy.
        wx.Yield()
        wx.BeginBusyCursor()

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

        # Clear the previous data.
        self.pipe_name.Clear()

        # The list of pipe names.
        for name in pipe_names():
            self.pipe_name.Append(str_to_gui(name))

        # Switch.
        if pipe_switch:
            # Switch data pipes.
            self.gui.interpreter.queue('pipe.switch', pipe)

            # Update the tree view.
            self.tree_panel.update()

        # Set the pipe name to the cdp.
        self.pipe_name.SetValue(str_to_gui(pipe))

        # Reset the cursor.
        wx.EndBusyCursor()
