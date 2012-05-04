###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
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

# Python module imports.
import wx

# relax module imports.
from status import Status; status = Status()
from user_functions.data import Uf_info; uf_info = Uf_info()

# relax GUI module imports.
from gui import paths
from gui.components.menu import build_menu_item
from gui.user_functions import User_functions


class Menu:
    """The menu bar GUI class."""

    # Some IDs for the menu entries.
    MENU_FILE_NEW = wx.NewId()
    MENU_FILE_CLOSE = wx.NewId()
    MENU_FILE_CLOSE_ALL = wx.NewId()
    MENU_FILE_OPEN = wx.NewId()
    MENU_FILE_SAVE = wx.NewId()
    MENU_FILE_SAVE_AS = wx.NewId()
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
    MENU_TOOLS_SYS_INFO = wx.NewId()
    MENU_HELP_MANUAL = wx.NewId()
    MENU_HELP_MAIL = wx.NewId()
    MENU_HELP_REFS = wx.NewId()
    MENU_HELP_GPL = wx.NewId()
    MENU_HELP_ABOUT_GUI = wx.NewId()
    MENU_HELP_ABOUT = wx.NewId()

    def __init__(self, gui):
        """Build the menu bar."""

        # Store the args.
        self.gui = gui

        # Create the menu bar GUI item.
        self.menubar = wx.MenuBar()

        # The 'File' menu entries.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_NEW, text="&New analysis\tCtrl+N", icon=paths.icon_16x16.new))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_CLOSE, text="&Close analysis", icon=paths.icon_16x16.document_close))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_CLOSE_ALL, text="&Close all analyses", icon=paths.icon_16x16.dialog_close))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_OPEN, text="&Open relax state\tCtrl+O", icon=paths.icon_16x16.document_open))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_SAVE, text="S&ave relax state\tCtrl+S", icon=paths.icon_16x16.document_save))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_SAVE_AS, text="Save as...\tCtrl+Shift+S", icon=paths.icon_16x16.document_save_as))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_FILE_EXIT, text="E&xit\tCtrl+Q", icon=paths.icon_16x16.exit))
        self.menubar.Append(menu, "&File")

        # The 'File' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.analysis.menu_new, id=self.MENU_FILE_NEW)
        self.gui.Bind(wx.EVT_MENU, self.gui.analysis.menu_close, id=self.MENU_FILE_CLOSE)
        self.gui.Bind(wx.EVT_MENU, self.gui.analysis.menu_close_all, id=self.MENU_FILE_CLOSE_ALL)
        self.gui.Bind(wx.EVT_MENU, self.gui.state_load, id=self.MENU_FILE_OPEN)
        self.gui.Bind(wx.EVT_MENU, self.gui.action_state_save, id=self.MENU_FILE_SAVE)
        self.gui.Bind(wx.EVT_MENU, self.gui.action_state_save_as, id=self.MENU_FILE_SAVE_AS)
        self.gui.Bind(wx.EVT_MENU, self.gui.exit_gui, id=self.MENU_FILE_EXIT)

        # The 'View' menu entries.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_VIEW_CONTROLLER, text="&Controller\tCtrl+Z", icon=paths.icon_16x16.preferences_system_performance))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_VIEW_SPIN_VIEW, text="&Spin view\tCtrl+T", icon=paths.icon_16x16.spin))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_VIEW_RESULTS, text="&Results viewer\tCtrl+R", icon=paths.icon_16x16.view_statistics))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_VIEW_PIPE_EDIT, text="&Data pipe editor\tCtrl+D", icon=paths.icon_16x16.pipe))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_VIEW_PROMPT, text="relax &prompt\tCtrl+P", icon=paths.icon_16x16.relax_prompt))
        self.menubar.Append(menu, "&View")

        # The 'View' actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.show_controller, id=self.MENU_VIEW_CONTROLLER)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_prompt, id=self.MENU_VIEW_PROMPT)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_tree, id=self.MENU_VIEW_SPIN_VIEW)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_results_viewer, id=self.MENU_VIEW_RESULTS)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_pipe_editor, id=self.MENU_VIEW_PIPE_EDIT)

        # The 'User functions' menu entries.
        self._user_functions_old()

        # The auto generated 'User functions' menu entries.
        self._user_functions()

        # The 'Tools' menu entries.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_TOOLS_FORMAT, text="&Free file format settings", icon=paths.icon_16x16.document_properties))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_TOOLS_SYS_INFO, text="System &information", icon=paths.icon_16x16.help_about))

        # The 'Tools->Test suite" sub-menu.
        test_suite_item = build_menu_item(menu, id=self.MENU_TOOLS_TEST_SUITE, text="&Test suite", icon=paths.icon_16x16.uf_script)
        sub_menu = wx.Menu()
        test_suite_item.SetSubMenu(sub_menu)
        sub_menu.AppendItem(build_menu_item(sub_menu, id=self.MENU_TOOLS_TEST_SUITE_ALL, text="&Full test suite", icon=paths.icon_16x16.uf_script))
        sub_menu.AppendSeparator()
        sub_menu.AppendItem(build_menu_item(sub_menu, id=self.MENU_TOOLS_TEST_SUITE_SYS, text="&System tests", icon=paths.icon_16x16.uf_script))
        sub_menu.AppendItem(build_menu_item(sub_menu, id=self.MENU_TOOLS_TEST_SUITE_UNIT, text="&Unit tests", icon=paths.icon_16x16.uf_script))
        sub_menu.AppendItem(build_menu_item(sub_menu, id=self.MENU_TOOLS_TEST_SUITE_GUI, text="&GUI tests", icon=paths.icon_16x16.uf_script))
        menu.AppendItem(test_suite_item)
        self.menubar.Append(menu, "&Tools")

        # The 'Tools' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.free_file_format_settings, id=self.MENU_TOOLS_FORMAT)
        self.gui.Bind(wx.EVT_MENU, self._sys_info, id=self.MENU_TOOLS_SYS_INFO)
        self.gui.Bind(wx.EVT_MENU, self.gui.run_test_suite, id=self.MENU_TOOLS_TEST_SUITE_ALL)
        self.gui.Bind(wx.EVT_MENU, self.gui.run_test_suite_sys, id=self.MENU_TOOLS_TEST_SUITE_SYS)
        self.gui.Bind(wx.EVT_MENU, self.gui.run_test_suite_unit, id=self.MENU_TOOLS_TEST_SUITE_UNIT)
        self.gui.Bind(wx.EVT_MENU, self.gui.run_test_suite_gui, id=self.MENU_TOOLS_TEST_SUITE_GUI)

        # The 'Help' menu entries.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_HELP_MANUAL, text="relax user &manual\tF1", icon=paths.icon_16x16.manual))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_HELP_MAIL, text="Mailing list &contact (relax-users@gna.org)", icon=paths.icon_16x16.contact))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_HELP_REFS, text="&References", icon=paths.icon_16x16.ref))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_HELP_GPL, text="&Licence", icon=paths.icon_16x16.gnu_head))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=self.MENU_HELP_ABOUT_GUI, text="About relaxG&UI", icon=paths.icon_16x16.about_relaxgui))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_HELP_ABOUT, text="About rela&x", icon=paths.icon_16x16.about_relax))
        self.menubar.Append(menu, "&Help")

        # The 'Help' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.relax_manual, id=self.MENU_HELP_MANUAL)
        self.gui.Bind(wx.EVT_MENU, self.gui.contact_relax, id=self.MENU_HELP_MAIL)
        self.gui.Bind(wx.EVT_MENU, self.gui.references, id=self.MENU_HELP_REFS)
        self.gui.Bind(wx.EVT_MENU, self._licence, id=self.MENU_HELP_GPL)
        self.gui.Bind(wx.EVT_MENU, self.gui.about_gui, id=self.MENU_HELP_ABOUT_GUI)
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

        # The user functions.
        user_functions = User_functions(self.gui)

        # Launch the user functions.
        user_functions.gpl.run()

        # Show the relax controller.
        self.gui.show_controller(event)


    def _sys_info(self, event):
        """Show the full system information using the sys_info user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The user functions.
        user_functions = User_functions(self.gui)

        # Launch the user functions.
        user_functions.sys_info.sys_info()


    def _user_functions(self):
        """Auto-generate the user function sub-menu."""

        # The menu.
        menu = wx.Menu()

        # Initialise some variables.
        class_list = []

        # The user functions.
        user_functions = User_functions(self.gui)

        # Loop over the user functions.
        for name, data in uf_info.uf_loop():
            # Split up the name.
            class_name, uf_name = split(name, '.')

            # Generate a submenu.
            if class_name not in class_list:
                # Get the user function class data object.
                data = uf_info.get_class(class_name)

                # Create a unique ID.
                class_id = wx.NewId()

                # Create the submenu.
                menu.AppendItem(build_menu_item(menu, id=class_id, text=data.menu_text, icon=fetch_icon(data.gui_icon)))

        # Add the menu.
        uf_menus = Uf_menus(parent=self.gui, menu=menu)

        # Add the sub-menu.
        title = "&User functions"
        self.menubar.Append(menu, title)
        self.menu_uf_id = self.menubar.FindMenu(title)


    def _user_functions_old(self):
        """Build the user function sub-menu."""

        # The menu.
        menu = wx.Menu()

        # Add the menu.
        uf_menus = Uf_menus(parent=self.gui, menu=menu)

        # Add the sub-menu.
        title = "&User functions old"
        self.menubar.Append(menu, title)
        self.menu_uf_id = self.menubar.FindMenu(title)


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

        # Loop over the user function menu items.
        menu = self.menubar.GetMenu(self.menu_uf_id)
        for item in menu.GetMenuItems():
            # Enable/disable.
            item.Enable(enable)

            # Sub-menu.
            submenu = item.GetSubMenu()
            if submenu:
                for subitem in submenu.GetMenuItems():
                    subitem.Enable(enable)



class Uf_menus:
    """A class for the creation of specialised menu entries for the user functions."""

    def __init__(self, parent=None, menu=None):
        """Set up the menu entries.

        @keyword parent:    The parent window.
        @type parent:       wx.Window instance
        @keyword menu:      The menu to add to.
        @type menu:         wx.Menu instance
        """

        # Store the args.
        self.parent = parent
        self.menu = menu

        # The user functions.
        user_functions = User_functions(self.parent)

        # Initialise some data structures.
        self.uf_names = {}
        self.uf = {}

        # Build the user function menus.
        id = self.add_class(name="bmrb", text="&bmrb", icon=paths.icon_16x16.bmrb)
        self.add_uf(parent_id=id, name="bmrb.citation", text="&citation", fn=user_functions.bmrb.citation)

        id = self.add_class(name="bruker", text="&bruker", icon=paths.icon_16x16.bruker)
        self.add_uf(parent_id=id, name="bruker.read", text="&read", icon=paths.icon_16x16.open, fn=user_functions.bruker.read)

        id = self.add_class(name="deselect", text="&deselect", icon=None)
        self.add_uf(parent_id=id, name="deselect.all", text="&all", icon=None, fn=user_functions.deselect.all)
        self.add_uf(parent_id=id, name="deselect.read", text="&read", icon=paths.icon_16x16.open, fn=user_functions.deselect.read)
        self.add_uf(parent_id=id, name="deselect.reverse", text="re&verse", icon=None, fn=user_functions.deselect.reverse)
        self.add_uf(parent_id=id, name="deselect.spin", text="&spin", icon=paths.icon_16x16.spin, fn=user_functions.deselect.spin)

        self.add_uf(parent_id=None, name="gpl", text="&gpl", icon=paths.icon_16x16.gnu_head, fn=user_functions.gpl.run)

        id = self.add_class(name="grace", text="gra&ce", icon=paths.icon_16x16.grace)
        self.add_uf(parent_id=id, name="grace.view", text="&view", icon=paths.icon_16x16.grace, fn=user_functions.grace.view)
        self.add_uf(parent_id=id, name="grace.write", text="&write", icon=paths.icon_16x16.save, fn=user_functions.grace.write)

        id = self.add_class(name="molecule", text="&molecule", icon=paths.icon_16x16.molecule)
        self.add_uf(parent_id=id, name="molecule.copy", text="&copy", icon=paths.icon_16x16.copy, fn=user_functions.molecule.copy)
        self.add_uf(parent_id=id, name="molecule.create", text="crea&te", icon=paths.icon_16x16.add, fn=user_functions.molecule.create)
        self.add_uf(parent_id=id, name="molecule.delete", text="&delete", icon=paths.icon_16x16.remove, fn=user_functions.molecule.delete)

        id = self.add_class(name="molmol", text="&molmol", icon=paths.icon_16x16.molmol)
        self.add_uf(parent_id=id, name="molmol.clear_history", text="clear_&history", icon=None, fn=user_functions.molmol.clear_history)
        self.add_uf(parent_id=id, name="molmol.command", text="&command", icon=None, fn=user_functions.molmol.command)
        self.add_uf(parent_id=id, name="molmol.macro_apply", text="&macro_apply", icon=paths.icon_16x16.molmol, fn=user_functions.molmol.macro_apply)
        self.add_uf(parent_id=id, name="molmol.macro_run", text="macro_&run", icon=paths.icon_16x16.open, fn=user_functions.molmol.macro_run)
        self.add_uf(parent_id=id, name="molmol.macro_write", text="macro_&write", icon=paths.icon_16x16.save, fn=user_functions.molmol.macro_write)
        self.add_uf(parent_id=id, name="molmol.ribbon", text="ri&bbon", icon=None, fn=user_functions.molmol.ribbon)
        self.add_uf(parent_id=id, name="molmol.tensor_pdb", text="&tensor_pdb", icon=None, fn=user_functions.molmol.tensor_pdb)
        self.add_uf(parent_id=id, name="molmol.view", text="&view", icon=None, fn=user_functions.molmol.view)

        id = self.add_class(name="noe", text="&noe", icon=None)
        self.add_uf(parent_id=id, name="noe.read_restraints", text="&read_restraints", icon=paths.icon_16x16.open, fn=user_functions.noe.read_restraints)
        self.add_uf(parent_id=id, name="noe.spectrum_type", text="&spectrum_type", icon=None, fn=user_functions.noe.spectrum_type)

        id = self.add_class(name="pipe", text="&pipe", icon=paths.icon_16x16.pipe)
        self.add_uf(parent_id=id, name="pipe.copy", text="&copy", icon=paths.icon_16x16.copy, fn=user_functions.pipe.copy)
        self.add_uf(parent_id=id, name="pipe.create", text="crea&te", icon=paths.icon_16x16.add, fn=user_functions.pipe.create)
        self.add_uf(parent_id=id, name="pipe.delete", text="&delete", icon=paths.icon_16x16.remove, fn=user_functions.pipe.delete)
        self.add_uf(parent_id=id, name="pipe.hybridise", text="&hybridise", icon=paths.icon_16x16.pipe_hybrid, fn=user_functions.pipe.hybridise)
        self.add_uf(parent_id=id, name="pipe.switch", text="&switch", icon=paths.icon_16x16.pipe_switch, fn=user_functions.pipe.switch)

        id = self.add_class(name="pymol", text="&pymol", icon=paths.icon_16x16.pymol)
        self.add_uf(parent_id=id, name="pymol.clear_history", text="clear_&history", icon=None, fn=user_functions.pymol.clear_history)
        self.add_uf(parent_id=id, name="pymol.command", text="&command", icon=None, fn=user_functions.pymol.command)
        self.add_uf(parent_id=id, name="pymol.macro_apply", text="&macro_apply", icon=paths.icon_16x16.pymol, fn=user_functions.pymol.macro_apply)
        self.add_uf(parent_id=id, name="pymol.macro_run", text="&macro_&run", icon=paths.icon_16x16.open, fn=user_functions.pymol.macro_run)
        self.add_uf(parent_id=id, name="pymol.macro_write", text="macro_&write", icon=paths.icon_16x16.save, fn=user_functions.pymol.macro_write)
        self.add_uf(parent_id=id, name="pymol.ribbon", text="ri&bbon", icon=None, fn=user_functions.pymol.ribbon)
        self.add_uf(parent_id=id, name="pymol.tensor_pdb", text="&tensor_pdb", icon=None, fn=user_functions.pymol.tensor_pdb)
        self.add_uf(parent_id=id, name="pymol.view", text="&view", icon=None, fn=user_functions.pymol.view)

        id = self.add_class(name="relax_data", text="&relax_data", icon=paths.icon_16x16.relax_data)
        self.add_uf(parent_id=id, name="relax_data.delete", text="&delete", icon=paths.icon_16x16.remove, fn=user_functions.relax_data.delete)
        self.add_uf(parent_id=id, name="relax_data.read", text="&read", icon=paths.icon_16x16.open, fn=user_functions.relax_data.read)

        id = self.add_class(name="relax_fit", text="relax_&fit", icon=None)
        self.add_uf(parent_id=id, name="relax_fit.relax_time", text="&relax_time", icon=None, fn=user_functions.relax_fit.relax_time)
        self.add_uf(parent_id=id, name="relax_fit.select_model", text="&select_model", icon=None, fn=user_functions.relax_fit.select_model)

        id = self.add_class(name="residue", text="resid&ue", icon=paths.icon_16x16.residue)
        self.add_uf(parent_id=id, name="residue.copy", text="&copy", icon=paths.icon_16x16.copy, fn=user_functions.residue.copy)
        self.add_uf(parent_id=id, name="residue.create", text="crea&te", icon=paths.icon_16x16.add, fn=user_functions.residue.create)
        self.add_uf(parent_id=id, name="residue.delete", text="&delete", icon=paths.icon_16x16.remove, fn=user_functions.residue.delete)

        id = self.add_class(name="results", text="&results", icon=paths.icon_16x16.about_relax)
        self.add_uf(parent_id=id, name="results.display", text="&display", icon=None, fn=user_functions.results.display)
        self.add_uf(parent_id=id, name="results.read", text="&read", icon=paths.icon_16x16.open, fn=user_functions.results.read)
        self.add_uf(parent_id=id, name="results.write", text="&write", icon=paths.icon_16x16.save, fn=user_functions.results.write)

        self.add_uf(parent_id=None, name="script", text="s&cript", icon=paths.icon_16x16.uf_script, fn=user_functions.script.run)

        id = self.add_class(name="select", text="se&lect", icon=None)
        self.add_uf(parent_id=id, name="select.all", text="&all", icon=None, fn=user_functions.select.all)
        self.add_uf(parent_id=id, name="select.read", text="&read", icon=paths.icon_16x16.open, fn=user_functions.select.read)
        self.add_uf(parent_id=id, name="select.reverse", text="re&verse", icon=None, fn=user_functions.select.reverse)
        self.add_uf(parent_id=id, name="select.spin", text="&spin", icon=paths.icon_16x16.spin, fn=user_functions.select.spin)

        id = self.add_class(name="sequence", text="se&quence", icon=paths.icon_16x16.sequence)
        self.add_uf(parent_id=id, name="sequence.copy", text="&copy", icon=paths.icon_16x16.copy, fn=user_functions.sequence.copy)
        self.add_uf(parent_id=id, name="sequence.read", text="&read", icon=paths.icon_16x16.open, fn=user_functions.sequence.read)
        self.add_uf(parent_id=id, name="sequence.write", text="&write", icon=paths.icon_16x16.save, fn=user_functions.sequence.write)

        id = self.add_class(name="spectrum", text="s&pectrum", icon=None)
        self.add_uf(parent_id=id, name="spectrum.baseplane_rmsd", text="&baseplane_rmsd", icon=None, fn=user_functions.spectrum.baseplane_rmsd)
        self.add_uf(parent_id=id, name="spectrum.delete", text="&delete", icon=paths.icon_16x16.remove, fn=user_functions.spectrum.delete)
        self.add_uf(parent_id=id, name="spectrum.error_analysis", text="&error_analysis", icon=None, fn=user_functions.spectrum.error_analysis)
        self.add_uf(parent_id=id, name="spectrum.integration_points", text="&integration_points", icon=None, fn=user_functions.spectrum.integration_points)
        self.add_uf(parent_id=id, name="spectrum.read_intensities", text="&read_intensities", icon=paths.icon_16x16.open, fn=user_functions.spectrum.read_intensities)
        self.add_uf(parent_id=id, name="spectrum.replicated", text="&replicated", icon=None, fn=user_functions.spectrum.replicated)

        id = self.add_class(name="spin", text="&spin", icon=paths.icon_16x16.spin)
        self.add_uf(parent_id=id, name="spin.copy", text="&copy", icon=paths.icon_16x16.copy, fn=user_functions.spin.copy)
        self.add_uf(parent_id=id, name="spin.create", text="crea&te", icon=paths.icon_16x16.add, fn=user_functions.spin.create)
        self.add_uf(parent_id=id, name="spin.create_pseudo", text="create_&pseudo", icon=paths.icon_16x16.add, fn=user_functions.spin.create_pseudo)
        self.add_uf(parent_id=id, name="spin.delete", text="&delete", icon=paths.icon_16x16.remove, fn=user_functions.spin.delete)
        self.add_uf(parent_id=id, name="spin.display", text="displa&y", icon=None, fn=user_functions.spin.display)
        self.add_uf(parent_id=id, name="spin.element", text="&element", icon=None, fn=user_functions.spin.element)
        self.add_uf(parent_id=id, name="spin.name", text="&name", icon=None, fn=user_functions.spin.name)
        self.add_uf(parent_id=id, name="spin.number", text="num&ber", icon=None, fn=user_functions.spin.number)

        id = self.add_class(name="structure", text="s&tructure", icon=paths.icon_16x16.structure)
        self.add_uf(parent_id=id, name="structure.create_diff_tensor_pdb", text="&create_diff_tensor_pdb", icon=None, fn=user_functions.structure.create_diff_tensor_pdb)
        self.add_uf(parent_id=id, name="structure.create_vector_dist", text="&create_vector_dist", icon=None, fn=user_functions.structure.create_vector_dist)
        self.add_uf(parent_id=id, name="structure.delete", text="&delete", icon=paths.icon_16x16.remove, fn=user_functions.structure.delete)
        self.add_uf(parent_id=id, name="structure.get_pos", text="&get_pos", icon=None, fn=user_functions.structure.get_pos)
        self.add_uf(parent_id=id, name="structure.load_spins", text="&load_spins", icon=paths.icon_16x16.spin, fn=user_functions.structure.load_spins)
        self.add_uf(parent_id=id, name="structure.read_pdb", text="&read_pdb", icon=paths.icon_16x16.open, fn=user_functions.structure.read_pdb)
        self.add_uf(parent_id=id, name="structure.read_xyz", text="&read_xyz", icon=paths.icon_16x16.open, fn=user_functions.structure.read_xyz)
        self.add_uf(parent_id=id, name="structure.vectors", text="&vectors", icon=None, fn=user_functions.structure.vectors)
        self.add_uf(parent_id=id, name="structure.write_pdb", text="&write_pdb", icon=paths.icon_16x16.save, fn=user_functions.structure.write_pdb)

        self.add_uf(parent_id=None, name="sys_info", text="sys_&info", icon=paths.icon_16x16.help_about, fn=user_functions.sys_info.sys_info)

        id = self.add_class(name="value", text="&value", icon=paths.icon_16x16.value)
        self.add_uf(parent_id=id, name="value.set", text="&set", icon=paths.icon_16x16.add, fn=user_functions.value.set)


    def add_class(self, name=None, text=None, icon=None):
        """Add the user function.

        @keyword name:      The name of the user function, such as 'residue.delete'.
        @type name:         str
        @keyword text:      The menu text string.
        @type text:         str
        @keyword icon:      The path to the icon image file for the menu entry.
        @type icon:         str or None
        @return:            The menu ID number.
        @rtype:             long
        """

        # Generate a unique ID.
        id = wx.NewId()

        # Build the menu entry.
        menu_item = build_menu_item(self.menu, id=id, text=text, icon=icon)

        # The sub-menu.
        sub_menu = wx.Menu()
        menu_item.SetSubMenu(sub_menu)

        # Append to the main menu item.
        self.menu.AppendItem(menu_item)

        # Return the ID.
        return id


    def add_uf(self, parent_id=None, name=None, text=None, icon=None, fn=None):
        """Add the user function.

        @keyword parent_id: The unique ID number of the parent menu entry.
        @type parent_id:    long
        @keyword name:      The name of the user function, such as 'residue.delete'.
        @type name:         str
        @keyword text:      The menu text string.
        @type text:         str
        @keyword icon:      The path to the icon image file for the menu entry.
        @type icon:         str or None
        @keyword fn:        The user function to execute.
        @type fn:           func
        @return:            The menu ID number.
        @rtype:             long
        """

        # Generate a unique ID.
        id = wx.NewId()

        # Store the data.
        self.uf_names[id] = name
        self.uf[id] = fn

        # Build the menu entry.
        if parent_id != None:
            sub_menu = self.menu.FindItemById(parent_id).GetSubMenu()
            item = build_menu_item(sub_menu, id=id, text=text, icon=icon)
            sub_menu.AppendItem(item)

        # No parent menu.
        else:
            item = build_menu_item(self.menu, id=id, text=text, icon=icon)
            self.menu.AppendItem(item)

        # Menu actions.
        self.parent.Bind(wx.EVT_MENU, self.call, id=id)

        # Return the ID.
        return id


    def call(self, event):
        """Execute the given user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Get the ID.
        id = event.GetId()

        # Call the user function.
        apply(self.uf[id])
