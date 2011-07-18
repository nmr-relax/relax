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

# GUI module imports.
from gui import paths
from gui.misc import gui_to_str
from gui.spin_viewer.splitter import Tree_splitter


class Spin_view_window(wx.Frame):
    """A window element for the tree view."""

    def __init__(self, *args, **kwds):
        """Set up the relax prompt."""

        # Store the parent object.
        self.gui = kwds.pop('parent')

        # Create GUI elements
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        # Some default values.
        self.size_x = 1200
        self.size_y = 800

        # Set up the window.
        sizer = self.setup_window()

        # Create a menu.
        self._create_menu()

        # Build the toolbar.
        self.toolbar()

        # The splitter window.
        splitter = Tree_splitter(self.gui, self, -1)
        sizer.Add(splitter, 1, wx.EXPAND|wx.ALL, 0)


    def _create_menu(self):
        """Build a menu for the window."""

        # Create the menu bar GUI item and add it to the main frame.
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)

        # The sequence menu entry.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&copy", icon=paths.icon_16x16.copy, fn=self.gui.user_functions.sequence.copy))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&read", icon=paths.icon_16x16.open, fn=self.gui.user_functions.sequence.read))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&write", icon=paths.icon_16x16.save, fn=self.gui.user_functions.sequence.write))
        self.menubar.Append(menu, "se&quence")

        # The structure menu entry.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&delete", icon=paths.icon_16x16.remove, fn=self.gui.user_functions.structure.delete))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&load_spins", icon=paths.icon_16x16.spin, fn=self.gui.user_functions.structure.load_spins))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&read_pdb", icon=paths.icon_16x16.open, fn=self.gui.user_functions.structure.read_pdb))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&write_pdb", icon=paths.icon_16x16.save, fn=self.gui.user_functions.structure.write_pdb))
        self.menubar.Append(menu, "st&ructure")

        # The molecule menu entry.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&copy", icon=paths.icon_16x16.copy, fn=self.gui.user_functions.molecule.copy))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="crea&te", icon=paths.icon_16x16.add, fn=self.gui.user_functions.molecule.create))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&delete", icon=paths.icon_16x16.remove, fn=self.gui.user_functions.molecule.delete))
        self.menubar.Append(menu, "&molecule")

        # The residue menu entry.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&copy", icon=paths.icon_16x16.copy, fn=self.gui.user_functions.residue.copy))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="crea&te", icon=paths.icon_16x16.add, fn=self.gui.user_functions.residue.create))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&delete", icon=paths.icon_16x16.remove, fn=self.gui.user_functions.residue.delete))
        self.menubar.Append(menu, "&residue")

        # The spin menu entry.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&copy", icon=paths.icon_16x16.copy, fn=self.gui.user_functions.spin.copy))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="crea&te", icon=paths.icon_16x16.add, fn=self.gui.user_functions.spin.create))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="create_&pseudo", icon=paths.icon_16x16.add, fn=self.gui.user_functions.spin.create_pseudo))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&delete", icon=paths.icon_16x16.remove, fn=self.gui.user_functions.spin.delete))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="displa&y", icon=None, fn=self.gui.user_functions.spin.display))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&element", icon=None, fn=self.gui.user_functions.spin.element))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&name", icon=None, fn=self.gui.user_functions.spin.name))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="num&ber", icon=None, fn=self.gui.user_functions.spin.number))
        self.menubar.Append(menu, "&spin")

        # The select menu entry.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&all", icon=None, fn=self.gui.user_functions.select.all))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&read", icon=paths.icon_16x16.open, fn=self.gui.user_functions.select.read))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="re&verse", icon=None, fn=self.gui.user_functions.select.reverse))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&spin", icon=paths.icon_16x16.spin, fn=self.gui.user_functions.select.spin))
        self.menubar.Append(menu, "se&lect")

        # The deselect menu entry.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&all", icon=None, fn=self.gui.user_functions.deselect.all))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&read", icon=paths.icon_16x16.open, fn=self.gui.user_functions.deselect.read))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="re&verse", icon=None, fn=self.gui.user_functions.deselect.reverse))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&spin", icon=paths.icon_16x16.spin, fn=self.gui.user_functions.deselect.spin))
        self.menubar.Append(menu, "&deselect")


    def Show(self, show=True):
        """Change the behaviour of showing the window to update the content.

        @keyword show:  A flag which is True shows the window.
        @type show:     bool
        """

        # Initialise observer name.
        self.name = 'spin view refresh'

        # Register a few methods in the observer objects.
        status.observers.uf_gui.register(self.name, self.refresh)
        status.observers.pipe_switch.register(self.name, self.refresh)

        # First update.
        self.refresh()

        # Then show the window using the baseclass method.
        if status.show_gui:
            wx.Frame.Show(self, show)


    def refresh(self, event=None):
        """Event handler for the refresh action.

        @param event:   The wx event.
        @type event:    wx event
        """

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
        status.observers.uf_gui.unregister(self.name)
        status.observers.pipe_switch.unregister(self.name)

        # Close the window.
        self.Hide()


    def setup_window(self):
        """Set up the window.

        @return:    The sizer object.
        @rtype:     wx.Sizer instance
        """

        # Set the frame title.
        self.SetTitle("The molecule, residue, and spin window")

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
            self.pipe_name.Append(name)

        # Switch.
        if pipe_switch:
            # Switch data pipes.
            self.gui.interpreter.pipe.switch(pipe)

            # Update the tree view.
            self.tree_panel.update()

        # Set the pipe name to the cdp.
        self.pipe_name.SetValue(pipe)

        # Reset the cursor.
        wx.EndBusyCursor()
