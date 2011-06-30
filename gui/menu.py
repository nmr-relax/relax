###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
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
"""Module for the main relax menu bar."""

# relax module imports.
from status import Status

# Python module imports.
import wx

# relax GUI module imports.
from gui import paths


class Menu:
    """The menu bar GUI class."""

    def __init__(self, gui):
        """Build the menu bar."""

        # Store the args.
        self.gui = gui

        # Create the menu bar GUI item and add it to the main frame.
        self.menubar = wx.MenuBar()
        self.gui.SetMenuBar(self.menubar)

        # The 'File' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_item(menu, id=1, text="&New analysis\tCtrl+N", icon=paths.icon_16x16.new))
        menu.AppendItem(self.build_menu_item(menu, id=6, text="&Close analysis", icon=paths.icon_16x16.document_close))
        menu.AppendItem(self.build_menu_item(menu, id=7, text="&Close all analyses", icon=paths.icon_16x16.dialog_close))
        menu.AppendSeparator()
        menu.AppendItem(self.build_menu_item(menu, id=2, text="&Open relax state\tCtrl+O", icon=paths.icon_16x16.open))
        menu.AppendItem(self.build_menu_item(menu, id=3, text="S&ave relax state\tCtrl+S", icon=paths.icon_16x16.save))
        menu.AppendItem(self.build_menu_item(menu, id=4, text="Save as...\tCtrl+Shift+S", icon=paths.icon_16x16.save_as))
        menu.AppendSeparator()
        menu.AppendItem(self.build_menu_item(menu, id=5, text="E&xit\tCtrl+Q", icon=paths.icon_16x16.exit))
        self.menubar.Append(menu, "&File")

        # The 'File' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.analysis.menu_new,              id=1)
        self.gui.Bind(wx.EVT_MENU, self.gui.analysis.menu_close,            id=6)
        self.gui.Bind(wx.EVT_MENU, self.gui.analysis.menu_close_all,        id=7)
        self.gui.Bind(wx.EVT_MENU, self.gui.state_load,                     id=2)
        self.gui.Bind(wx.EVT_MENU, self.gui.action_state_save,              id=3)
        self.gui.Bind(wx.EVT_MENU, self.gui.action_state_save_as,           id=4)
        self.gui.Bind(wx.EVT_MENU, self.gui.exit_gui,                       id=5)

        # The 'View' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_item(menu, id=50, text="&Controller\tCtrl+Z", icon=paths.icon_16x16.controller))
        menu.AppendItem(self.build_menu_item(menu, id=51, text="relax &prompt\tCtrl+P", icon=paths.icon_16x16.relax_prompt))
        menu.AppendItem(self.build_menu_item(menu, id=52, text="&Spin view\tCtrl+T", icon=paths.icon_16x16.spin))
        menu.AppendItem(self.build_menu_item(menu, id=53, text="&Results viewer\tCtrl+R", icon=paths.icon_16x16.view_statistics))
        self.menubar.Append(menu, "&View")

        # The 'View' actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.show_controller,                id=50)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_prompt,                    id=51)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_tree,                      id=52)
        self.gui.Bind(wx.EVT_MENU, self.gui.analysis.show_results_viewer,   id=53)

        # The 'User functions' menu entries.
        self._user_functions()

        # The 'Settings' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_item(menu, id=20, text="&Global relax settings", icon=paths.icon_16x16.settings_global))
        menu.AppendItem(self.build_menu_item(menu, id=21, text="&Free file format settings", icon=paths.icon_16x16.settings))
        menu.AppendItem(self.build_menu_item(menu, id=22, text="Reset a&ll settings", icon=paths.icon_16x16.settings_reset))
        self.menubar.Append(menu, "&Settings")

        # The 'Settings' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.global_parameters,         id=20)
        self.gui.Bind(wx.EVT_MENU, self.gui.free_file_format_settings, id=21)
        self.gui.Bind(wx.EVT_MENU, self.gui.reset_setting,             id=22)

        # The 'Help' menu entries.
        menu = wx.Menu()
        menu.AppendItem(self.build_menu_item(menu, id=40, text="relax user &manual\tF1", icon=paths.icon_16x16.manual))
        menu.AppendSeparator()
        menu.AppendItem(self.build_menu_item(menu, id=41, text="Mailing list &contact (relax-users@gna.org)", icon=paths.icon_16x16.contact))
        menu.AppendItem(self.build_menu_item(menu, id=42, text="&References", icon=paths.icon_16x16.ref))
        menu.AppendSeparator()
        menu.AppendItem(self.build_menu_item(menu, id=43, text="About relaxG&UI", icon=paths.icon_16x16.about_relaxgui))
        menu.AppendItem(self.build_menu_item(menu, id=44, text="About rela&x", icon=paths.icon_16x16.about_relax))
        self.menubar.Append(menu, "&Help")

        # The 'Help' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.relax_manual,   id=40)
        self.gui.Bind(wx.EVT_MENU, self.gui.contact_relax,  id=41)
        self.gui.Bind(wx.EVT_MENU, self.gui.references,     id=42)
        self.gui.Bind(wx.EVT_MENU, self.gui.about_gui,      id=43)
        self.gui.Bind(wx.EVT_MENU, self.gui.about_relax,    id=44)

        # Menu update.
        self.gui.Bind(wx.EVT_MENU_OPEN, self.update_menus)


    def build_menu_item(self, menu, parent=None, id=None, text='', tooltip='', icon=None, fn=None):
        """Construct and return the menu sub-item.

        @param menu:        The menu object to place this entry in.
        @type menu:         wx.Menu instance
        @keyword id:        The element identification number.
        @type id:           int
        @keyword text:      The text for the menu entry.
        @type text:         None or str
        @keyword tooltip:   A tool tip.
        @type tooltip:      str
        @keyword icon:      The bitmap icon path.
        @type icon:         None or str
        @keyword fn:        The function to bind to the menu entry.
        @type fn:           class method
        @return:            The initialised wx.MenuItem() instance.
        @rtype:             wx.MenuItem() instance
        """

        # A new ID if necessary.
        if id == None:
            id = wx.NewId()

        # Initialise the GUI element.
        element = wx.MenuItem(menu, id, text, tooltip)

        # Set the icon.
        if icon:
            element.SetBitmap(wx.Bitmap(icon))

        # Bind the menu entry.
        if fn and parent:
            parent.Bind(wx.EVT_MENU, fn, id=id)

        # Return the element.
        return element


    def _create_menu(self, menu, entries):
        """Build the menu."""

        # Loop over the menu entries.
        for item in entries:
            # Build the menu entry.
            menu_item = self.build_menu_item(menu, id=item[0], text=item[1], icon=item[2])

            # A sub-menu.
            if len(item[4]):
                # The sub-menu.
                sub_menu = wx.Menu()

                # Loop over the sub-menus.
                for sub_item in item[4]:
                    # Build the menu entry.
                    sub_menu_item = self.build_menu_item(sub_menu, id=sub_item[0], text=sub_item[1], icon=sub_item[2])
                    sub_menu.AppendItem(sub_menu_item)

                    # The menu actions.
                    self.gui.Bind(wx.EVT_MENU, sub_item[3], id=sub_item[0])

                # Append the sub-menu.
                menu_item.SetSubMenu(sub_menu)

            # A normal menu item.
            else:
                # The menu actions.
                self.gui.Bind(wx.EVT_MENU, item[3], id=item[0])

            # Append the menu item.
            menu.AppendItem(menu_item)


    def _user_functions(self):
        """Build the user function sub-menu."""

        # The menu.
        menu = wx.Menu()

        # The list of entries to build.
        self.entries_uf = [
            [wx.NewId(), "&molecule", paths.icon_16x16.molecule, None, [
                [wx.NewId(), "&copy",   paths.icon_16x16.copy, self.gui.user_functions.molecule.copy],
                [wx.NewId(), "crea&te", paths.icon_16x16.add, self.gui.user_functions.molecule.create],
                [wx.NewId(), "&delete", paths.icon_16x16.remove, self.gui.user_functions.molecule.delete]
            ]],
            [wx.NewId(), "&pipe", paths.icon_16x16.pipe, None, [
                [wx.NewId(), "&copy",   paths.icon_16x16.copy, self.gui.user_functions.pipes.copy],
                [wx.NewId(), "crea&te", paths.icon_16x16.add, self.gui.user_functions.pipes.create],
                [wx.NewId(), "&delete", paths.icon_16x16.remove, self.gui.user_functions.pipes.delete],
                [wx.NewId(), "&switch", paths.icon_16x16.pipe_switch, self.gui.user_functions.pipes.switch]
            ]],
            [wx.NewId(), "&relax_data", paths.icon_16x16.relax_data, None, [
                [wx.NewId(), "&delete", paths.icon_16x16.remove, self.gui.user_functions.relax_data.delete],
                [wx.NewId(), "&read",   paths.icon_16x16.open, self.gui.user_functions.relax_data.read]
            ]],
            [wx.NewId(), "resid&ue", paths.icon_16x16.residue, None, [
                [wx.NewId(), "&copy",   paths.icon_16x16.copy, self.gui.user_functions.residue.copy],
                [wx.NewId(), "crea&te", paths.icon_16x16.add, self.gui.user_functions.residue.create],
                [wx.NewId(), "&delete", paths.icon_16x16.remove, self.gui.user_functions.residue.delete]
            ]],
            [wx.NewId(), "s&cript",   paths.icon_16x16.uf_script, self.gui.user_functions.script.run, []],
            [wx.NewId(), "se&quence", paths.icon_16x16.sequence, None, [
                [wx.NewId(), "&read", paths.icon_16x16.open, self.gui.user_functions.sequence.read]
            ]],
            [wx.NewId(), "&spin", paths.icon_16x16.spin, None, [
                [wx.NewId(), "&copy",   paths.icon_16x16.copy, self.gui.user_functions.spin.copy],
                [wx.NewId(), "crea&te", paths.icon_16x16.add, self.gui.user_functions.spin.create],
                [wx.NewId(), "&delete", paths.icon_16x16.remove, self.gui.user_functions.spin.delete]
            ]],
            [wx.NewId(), "&value", paths.icon_16x16.value, None, [
                [wx.NewId(), "&set",   paths.icon_16x16.add, self.gui.user_functions.value.set]
            ]]
        ]

        # Build.
        self._create_menu(menu, self.entries_uf)

        # Add the sub-menu.
        title = "&User functions"
        self.menubar.Append(menu, title)
        self.menu_uf_id = self.menubar.FindMenu(title)


    def update_menus(self, event):
        """Update the menus dependent on the relax state.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The status object.
        status = Status()

        # Loop over the user function menu items.
        for i in range(len(self.entries_uf)):
            # Enable the menu entries.
            if not status.exec_lock.locked():
                self.menubar.Enable(self.entries_uf[i][0], True)

            # Disable the menu entries.
            else:
                self.menubar.Enable(self.entries_uf[i][0], False)
