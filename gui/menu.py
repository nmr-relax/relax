###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
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
"""The main relax menu bar."""

# Python module imports.
import sys
import wx

# relax module imports.
from graphics import fetch_icon
from gui.components.menu import build_menu_item
from gui.uf_objects import build_uf_menus, Uf_storage; uf_store = Uf_storage()
from status import Status; status = Status()
from user_functions.data import Uf_info; uf_info = Uf_info()


class Menu:
    """The menu bar GUI class."""

    # Some IDs for the menu entries.
    MENU_FILE_NEW = wx.NewId()
    MENU_FILE_CLOSE = wx.NewId()
    MENU_FILE_CLOSE_ALL = wx.NewId()
    MENU_FILE_OPEN = wx.NewId()
    MENU_FILE_SAVE = wx.NewId()
    MENU_FILE_SAVE_AS = wx.NewId()
    MENU_FILE_EXPORT_BMRB = wx.NewId()
    MENU_FILE_EXIT = wx.NewId()
    MENU_VIEW_CONTROLLER = wx.NewId()
    MENU_VIEW_SPIN_VIEW = wx.NewId()
    MENU_VIEW_RESULTS = wx.NewId()
    MENU_VIEW_PIPE_EDIT = wx.NewId()
    MENU_VIEW_PROMPT = wx.NewId()
    MENU_TOOLS_FORMAT = wx.NewId()
    MENU_TOOLS_TEST_SUITE = wx.NewId()
    MENU_TOOLS_TEST_SUITE_ALL = wx.NewId()
    MENU_TOOLS_TEST_SUITE_SYS = wx.NewId()
    MENU_TOOLS_TEST_SUITE_UNIT = wx.NewId()
    MENU_TOOLS_TEST_SUITE_GUI = wx.NewId()
    MENU_TOOLS_TEST_SUITE_VERIFICATION = wx.NewId()
    MENU_TOOLS_SYS_INFO = wx.NewId()
    MENU_HELP_MANUAL = wx.NewId()
    MENU_HELP_MAIL = wx.NewId()
    MENU_HELP_REFS = wx.NewId()
    MENU_HELP_GPL = wx.NewId()
    MENU_HELP_ABOUT = wx.NewId()

    def __init__(self, gui):
        """Build the menu bar."""

        # Store the args.
        self.gui = gui

        # Create the menu bar GUI item.
        self.menubar = wx.MenuBar()

        # The 'File' menu entries.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_NEW, text="&New analysis\tCtrl+N", icon=fetch_icon('oxygen.actions.document-new', "16x16")))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_CLOSE, text="&Close analysis", icon=fetch_icon('oxygen.actions.document-close', "16x16")))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_CLOSE_ALL, text="&Close all analyses", icon=fetch_icon('oxygen.actions.dialog-close', "16x16")))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_OPEN, text="&Open relax state\tCtrl+O", icon=fetch_icon('oxygen.actions.document-open', "16x16")))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_SAVE, text="S&ave relax state\tCtrl+S", icon=fetch_icon('oxygen.actions.document-save', "16x16")))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_SAVE_AS, text="Save as...\tCtrl+Shift+S", icon=fetch_icon('oxygen.actions.document-save-as', "16x16")))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_EXPORT_BMRB, text="Export for BMRB deposition", icon=fetch_icon('relax.bmrb')))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_EXIT, text="E&xit\tCtrl+Q", icon=fetch_icon('oxygen.actions.system-shutdown', "16x16")))
        self.menubar.Append(menu, "&File")

        # The 'File' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.analysis.menu_new, id=self.MENU_FILE_NEW)
        self.gui.Bind(wx.EVT_MENU, self.gui.analysis.menu_close, id=self.MENU_FILE_CLOSE)
        self.gui.Bind(wx.EVT_MENU, self.gui.analysis.menu_close_all, id=self.MENU_FILE_CLOSE_ALL)
        self.gui.Bind(wx.EVT_MENU, self.gui.state_load, id=self.MENU_FILE_OPEN)
        self.gui.Bind(wx.EVT_MENU, self.gui.action_state_save, id=self.MENU_FILE_SAVE)
        self.gui.Bind(wx.EVT_MENU, self.gui.action_state_save_as, id=self.MENU_FILE_SAVE_AS)
        self.gui.Bind(wx.EVT_MENU, self.gui.action_export_bmrb, id=self.MENU_FILE_EXPORT_BMRB)
        self.gui.Bind(wx.EVT_MENU, self.gui.exit_gui, id=self.MENU_FILE_EXIT)

        # The 'View' menu entries.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_VIEW_CONTROLLER, text="&Controller\tCtrl+Z", icon=fetch_icon('oxygen.apps.preferences-system-performance', "16x16")))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_VIEW_SPIN_VIEW, text="&Spin viewer\tCtrl+T", icon=fetch_icon('relax.spin', "16x16")))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_VIEW_RESULTS, text="&Results viewer\tCtrl+R", icon=fetch_icon('oxygen.actions.view-statistics', "16x16")))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_VIEW_PIPE_EDIT, text="&Data pipe editor\tCtrl+D", icon=fetch_icon('relax.pipe', "16x16")))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_VIEW_PROMPT, text="relax &prompt\tCtrl+P", icon=fetch_icon('oxygen.mimetypes.application-x-executable-script', "16x16")))
        self.menubar.Append(menu, "&View")

        # The 'View' actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.show_controller, id=self.MENU_VIEW_CONTROLLER)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_prompt, id=self.MENU_VIEW_PROMPT)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_tree, id=self.MENU_VIEW_SPIN_VIEW)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_results_viewer, id=self.MENU_VIEW_RESULTS)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_pipe_editor, id=self.MENU_VIEW_PIPE_EDIT)

        # The auto generated 'User functions' menu entries.
        self.menu_uf_ids = build_uf_menus(parent=self.gui, menubar=self.menubar)

        # The 'Tools' menu entries.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_TOOLS_FORMAT, text="&Free file format settings", icon=fetch_icon('oxygen.actions.document-properties', "16x16")))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_TOOLS_SYS_INFO, text="System &information", icon=fetch_icon('oxygen.actions.help-about', "16x16")))

        # The 'Tools->Test suite" sub-menu.
        test_suite_item = build_menu_item(menu, id=self.MENU_TOOLS_TEST_SUITE, text="&Test suite", icon=fetch_icon('oxygen.mimetypes.application-x-desktop', "16x16"))
        sub_menu = wx.Menu()
        test_suite_item.SetSubMenu(sub_menu)
        sub_menu.AppendItem(build_menu_item(sub_menu, id=self.MENU_TOOLS_TEST_SUITE_ALL, text="&Full test suite", icon=fetch_icon('oxygen.mimetypes.application-x-desktop', "16x16")))
        sub_menu.AppendSeparator()
        sub_menu.AppendItem(build_menu_item(sub_menu, id=self.MENU_TOOLS_TEST_SUITE_SYS, text="&System tests", icon=fetch_icon('oxygen.mimetypes.application-x-desktop', "16x16")))
        sub_menu.AppendItem(build_menu_item(sub_menu, id=self.MENU_TOOLS_TEST_SUITE_UNIT, text="&Unit tests", icon=fetch_icon('oxygen.mimetypes.application-x-desktop', "16x16")))
        sub_menu.AppendItem(build_menu_item(sub_menu, id=self.MENU_TOOLS_TEST_SUITE_GUI, text="&GUI tests", icon=fetch_icon('oxygen.mimetypes.application-x-desktop', "16x16")))
        sub_menu.AppendItem(build_menu_item(sub_menu, id=self.MENU_TOOLS_TEST_SUITE_VERIFICATION, text="&Verification tests", icon=fetch_icon('oxygen.mimetypes.application-x-desktop', "16x16")))
        menu.AppendItem(test_suite_item)
        self.menubar.Append(menu, "&Tools")

        # The 'Tools' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.free_file_format_settings, id=self.MENU_TOOLS_FORMAT)
        self.gui.Bind(wx.EVT_MENU, self._sys_info, id=self.MENU_TOOLS_SYS_INFO)
        self.gui.Bind(wx.EVT_MENU, self.gui.run_test_suite, id=self.MENU_TOOLS_TEST_SUITE_ALL)
        self.gui.Bind(wx.EVT_MENU, self.gui.run_test_suite_sys, id=self.MENU_TOOLS_TEST_SUITE_SYS)
        self.gui.Bind(wx.EVT_MENU, self.gui.run_test_suite_unit, id=self.MENU_TOOLS_TEST_SUITE_UNIT)
        self.gui.Bind(wx.EVT_MENU, self.gui.run_test_suite_gui, id=self.MENU_TOOLS_TEST_SUITE_GUI)
        self.gui.Bind(wx.EVT_MENU, self.gui.run_test_suite_verification, id=self.MENU_TOOLS_TEST_SUITE_VERIFICATION)

        # The 'Help' menu entries.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_HELP_MANUAL, text="relax user &manual\tF1", icon=fetch_icon('oxygen.mimetypes.application-pdf', "16x16")))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_HELP_MAIL, text="Mailing list &contact (relax-users@gna.org)", icon=fetch_icon('oxygen.actions.mail-mark-unread-new', "16x16")))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_HELP_REFS, text="&References", icon=fetch_icon('oxygen.actions.flag-blue', "16x16")))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_HELP_GPL, text="&Licence", icon=fetch_icon('relax.gnu-head-mini', "16x16")))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_HELP_ABOUT, text="About rela&x", icon=fetch_icon("relax.relax")))
        self.menubar.Append(menu, "&Help")

        # The 'Help' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.relax_manual, id=self.MENU_HELP_MANUAL)
        self.gui.Bind(wx.EVT_MENU, self.gui.contact_relax, id=self.MENU_HELP_MAIL)
        self.gui.Bind(wx.EVT_MENU, self.gui.references, id=self.MENU_HELP_REFS)
        self.gui.Bind(wx.EVT_MENU, self._licence, id=self.MENU_HELP_GPL)
        self.gui.Bind(wx.EVT_MENU, self.gui.about_relax, id=self.MENU_HELP_ABOUT)

        # Add the menu bar GUI item to the main frame.
        if status.show_gui:
            self.gui.SetMenuBar(self.menubar)

        # Menu update.
        self.gui.Bind(wx.EVT_MENU_OPEN, self.update_menus)


    def _create_menu(self, menu, entries):
        """Build the menu."""

        # Loop over the menu entries.
        for item in entries:
            # Build the menu entry.
            menu_item = build_menu_item(menu, id=item[0], text=item[1], icon=item[2])

            # A sub-menu.
            if len(item[4]):
                # The sub-menu.
                sub_menu = wx.Menu()

                # Loop over the sub-menus.
                for sub_item in item[4]:
                    # Build the menu entry.
                    sub_menu_item = build_menu_item(sub_menu, id=sub_item[0], text=sub_item[1], icon=sub_item[2])
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


    def _licence(self, event):
        """Show the GPL licence.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Print the GPL to STDOUT.
        file = open('docs/COPYING')
        for line in file.readlines():
            sys.stdout.write(line)

        # Show the relax controller.
        self.gui.show_controller(event)


    def _sys_info(self, event):
        """Show the full system information using the sys_info user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Launch the user function.
        uf_store['sys_info']()


    def update_menus(self, event):
        """Update the menus dependent on the relax state.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The status object.
        status = Status()

        # Flag for enabling or disabling the menu entries.
        enable = False
        if not status.exec_lock.locked():
            enable = True

        # The file menu entries.
        self.menubar.Enable(self.MENU_FILE_NEW, enable)
        self.menubar.Enable(self.MENU_FILE_CLOSE, enable)
        self.menubar.Enable(self.MENU_FILE_CLOSE_ALL, enable)
        self.menubar.Enable(self.MENU_FILE_OPEN, enable)
        self.menubar.Enable(self.MENU_FILE_SAVE, enable)
        self.menubar.Enable(self.MENU_FILE_SAVE_AS, enable)

        # The view menu entries.
        self.menubar.Enable(self.MENU_VIEW_PROMPT, enable)

        # Loop over the user function menus.
        for id in self.menu_uf_ids:
            # Loop over the user function menu items.
            menu = self.menubar.GetMenu(id)
            for item in menu.GetMenuItems():
                # Enable/disable.
                item.Enable(enable)

                # Sub-menu.
                submenu = item.GetSubMenu()
                if submenu:
                    for subitem in submenu.GetMenuItems():
                        subitem.Enable(enable)
