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
from gui.components.menu import build_menu_item


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
        menu.AppendItem(build_menu_item(menu, id=1, text="&New analysis\tCtrl+N", icon=paths.icon_16x16.new))
        menu.AppendItem(build_menu_item(menu, id=6, text="&Close analysis", icon=paths.icon_16x16.document_close))
        menu.AppendItem(build_menu_item(menu, id=7, text="&Close all analyses", icon=paths.icon_16x16.dialog_close))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=2, text="&Open relax state\tCtrl+O", icon=paths.icon_16x16.open))
        menu.AppendItem(build_menu_item(menu, id=3, text="S&ave relax state\tCtrl+S", icon=paths.icon_16x16.save))
        menu.AppendItem(build_menu_item(menu, id=4, text="Save as...\tCtrl+Shift+S", icon=paths.icon_16x16.save_as))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=5, text="E&xit\tCtrl+Q", icon=paths.icon_16x16.exit))
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
        menu.AppendItem(build_menu_item(menu, id=50, text="&Controller\tCtrl+Z", icon=paths.icon_16x16.controller))
        menu.AppendItem(build_menu_item(menu, id=52, text="&Spin view\tCtrl+T", icon=paths.icon_16x16.spin))
        menu.AppendItem(build_menu_item(menu, id=53, text="&Results viewer\tCtrl+R", icon=paths.icon_16x16.view_statistics))
        menu.AppendItem(build_menu_item(menu, id=54, text="&Data pipe editor", icon=paths.icon_16x16.pipe))
        menu.AppendItem(build_menu_item(menu, id=51, text="relax &prompt\tCtrl+P", icon=paths.icon_16x16.relax_prompt))
        self.menubar.Append(menu, "&View")

        # The 'View' actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.show_controller,                id=50)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_prompt,                    id=51)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_tree,                      id=52)
        self.gui.Bind(wx.EVT_MENU, self.gui.analysis.show_results_viewer,   id=53)
        self.gui.Bind(wx.EVT_MENU, self.gui.show_pipe_editor,               id=54)

        # The 'User functions' menu entries.
        self._user_functions()

        # The 'Settings' menu entries.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, id=21, text="&Free file format settings", icon=paths.icon_16x16.document_properties))
        menu.AppendItem(build_menu_item(menu, id=22, text="Reset a&ll settings", icon=paths.icon_16x16.settings_reset))
        self.menubar.Append(menu, "&Settings")

        # The 'Settings' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.free_file_format_settings, id=21)
        self.gui.Bind(wx.EVT_MENU, self.gui.reset_setting,             id=22)

        # The 'Help' menu entries.
        menu = wx.Menu()
        menu.AppendItem(build_menu_item(menu, id=40, text="relax user &manual\tF1", icon=paths.icon_16x16.manual))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=41, text="Mailing list &contact (relax-users@gna.org)", icon=paths.icon_16x16.contact))
        menu.AppendItem(build_menu_item(menu, id=42, text="&References", icon=paths.icon_16x16.ref))
        menu.AppendSeparator()
        menu.AppendItem(build_menu_item(menu, id=43, text="About relaxG&UI", icon=paths.icon_16x16.about_relaxgui))
        menu.AppendItem(build_menu_item(menu, id=44, text="About rela&x", icon=paths.icon_16x16.about_relax))
        self.menubar.Append(menu, "&Help")

        # The 'Help' menu actions.
        self.gui.Bind(wx.EVT_MENU, self.gui.relax_manual,   id=40)
        self.gui.Bind(wx.EVT_MENU, self.gui.contact_relax,  id=41)
        self.gui.Bind(wx.EVT_MENU, self.gui.references,     id=42)
        self.gui.Bind(wx.EVT_MENU, self.gui.about_gui,      id=43)
        self.gui.Bind(wx.EVT_MENU, self.gui.about_relax,    id=44)

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


    def _user_functions(self):
        """Build the user function sub-menu."""

        # The menu.
        menu = wx.Menu()

        # The list of entries to build.
        self.entries_uf = [
            [wx.NewId(), "&deselect", None, None, [
                [wx.NewId(), "&all",    None, self.gui.user_functions.deselect.all],
                [wx.NewId(), "&read",   paths.icon_16x16.open, self.gui.user_functions.deselect.read],
                [wx.NewId(), "re&verse", None, self.gui.user_functions.deselect.reverse],
                [wx.NewId(), "&spin", paths.icon_16x16.spin, self.gui.user_functions.deselect.spin],
            ]],
            [wx.NewId(), "&molecule", paths.icon_16x16.molecule, None, [
                [wx.NewId(), "&copy",   paths.icon_16x16.copy, self.gui.user_functions.molecule.copy],
                [wx.NewId(), "crea&te", paths.icon_16x16.add, self.gui.user_functions.molecule.create],
                [wx.NewId(), "&delete", paths.icon_16x16.remove, self.gui.user_functions.molecule.delete]
            ]],
            [wx.NewId(), "&noe", None, None, [
                [wx.NewId(), "&read_restraints", paths.icon_16x16.open, self.gui.user_functions.noe.read_restraints],
                [wx.NewId(), "&spectrum_type",   None, self.gui.user_functions.noe.spectrum_type]
            ]],
            [wx.NewId(), "&pipe", paths.icon_16x16.pipe, None, [
                [wx.NewId(), "&copy",   paths.icon_16x16.copy, self.gui.user_functions.pipe.copy],
                [wx.NewId(), "crea&te", paths.icon_16x16.add, self.gui.user_functions.pipe.create],
                [wx.NewId(), "&delete", paths.icon_16x16.remove, self.gui.user_functions.pipe.delete],
                [wx.NewId(), "&switch", paths.icon_16x16.pipe_switch, self.gui.user_functions.pipe.switch]
            ]],
            [wx.NewId(), "&relax_data", paths.icon_16x16.relax_data, None, [
                [wx.NewId(), "&delete", paths.icon_16x16.remove, self.gui.user_functions.relax_data.delete],
                [wx.NewId(), "&read",   paths.icon_16x16.open, self.gui.user_functions.relax_data.read]
            ]],
            [wx.NewId(), "relax_&fit", None, None, [
                [wx.NewId(), "&relax_time", None, self.gui.user_functions.relax_fit.relax_time],
                [wx.NewId(), "&select_model", None,self.gui.user_functions.relax_fit.select_model]
            ]],
            [wx.NewId(), "resid&ue", paths.icon_16x16.residue, None, [
                [wx.NewId(), "&copy",   paths.icon_16x16.copy, self.gui.user_functions.residue.copy],
                [wx.NewId(), "crea&te", paths.icon_16x16.add, self.gui.user_functions.residue.create],
                [wx.NewId(), "&delete", paths.icon_16x16.remove, self.gui.user_functions.residue.delete]
            ]],
            [wx.NewId(), "s&cript",   paths.icon_16x16.uf_script, self.gui.user_functions.script.run, []],
            [wx.NewId(), "se&lect", None, None, [
                [wx.NewId(), "&all",    None, self.gui.user_functions.select.all],
                [wx.NewId(), "&read",   paths.icon_16x16.open, self.gui.user_functions.select.read],
                [wx.NewId(), "re&verse", None, self.gui.user_functions.select.reverse],
                [wx.NewId(), "&spin", paths.icon_16x16.spin, self.gui.user_functions.select.spin],
            ]],
            [wx.NewId(), "se&quence", paths.icon_16x16.sequence, None, [
                [wx.NewId(), "&copy",   paths.icon_16x16.copy, self.gui.user_functions.sequence.copy],
                [wx.NewId(), "&read", paths.icon_16x16.open, self.gui.user_functions.sequence.read],
                [wx.NewId(), "&write", paths.icon_16x16.save, self.gui.user_functions.sequence.write]
            ]],
            [wx.NewId(), "s&pectrum", None, None, [
                [wx.NewId(), "&baseplane_rmsd", None, self.gui.user_functions.spectrum.baseplane_rmsd],
                [wx.NewId(), "&error_analysis", None, self.gui.user_functions.spectrum.error_analysis],
                [wx.NewId(), "&integration_points", None, self.gui.user_functions.spectrum.integration_points],
                [wx.NewId(), "&read_intensities", paths.icon_16x16.open, self.gui.user_functions.spectrum.read_intensities],
                [wx.NewId(), "&replicated", None, self.gui.user_functions.spectrum.replicated]
            ]],
            [wx.NewId(), "&spin", paths.icon_16x16.spin, None, [
                [wx.NewId(), "&copy",   paths.icon_16x16.copy, self.gui.user_functions.spin.copy],
                [wx.NewId(), "crea&te", paths.icon_16x16.add, self.gui.user_functions.spin.create],
                [wx.NewId(), "create_&pseudo", paths.icon_16x16.add, self.gui.user_functions.spin.create_pseudo],
                [wx.NewId(), "&delete", paths.icon_16x16.remove, self.gui.user_functions.spin.delete],
                [wx.NewId(), "displa&y", None, self.gui.user_functions.spin.display],
                [wx.NewId(), "&element", None, self.gui.user_functions.spin.element],
                [wx.NewId(), "&name", None, self.gui.user_functions.spin.name],
                [wx.NewId(), "num&ber", None, self.gui.user_functions.spin.number]
            ]],
            [wx.NewId(), "s&tructure", paths.icon_16x16.structure, None, [
                [wx.NewId(), "&delete", paths.icon_16x16.remove, self.gui.user_functions.structure.delete],
                [wx.NewId(), "&load_spins", paths.icon_16x16.spin, self.gui.user_functions.structure.load_spins],
                [wx.NewId(), "&read_pdb", paths.icon_16x16.open, self.gui.user_functions.structure.read_pdb],
                [wx.NewId(), "&write_pdb", paths.icon_16x16.save, self.gui.user_functions.structure.write_pdb]
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
