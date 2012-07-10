###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Michael Bieri                                       #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing the classes for GUI components involving molecules."""

# Python module imports.
import wx
import wx.lib.buttons

# relax module imports.
from generic_fns.mol_res_spin import molecule_loop, return_molecule
from graphics import fetch_icon
from status import Status; status = Status()
from user_functions.data import Uf_info; uf_info = Uf_info()

# relax GUI module imports.
from gui.components.base_list import Base_list
from gui.string_conv import gui_to_str, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()


class Molecule(Base_list):
    """The GUI element for listing loaded molecules."""

    def action_bmrb_thiol_state(self, event):
        """Launch the bmrb.thiol_state user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The current state.
        state = None
        if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'thiol_state'):
            state = cdp.exp_info.thiol_state

        # Launch the dialog.
        if state == None:
            uf_store['bmrb.thiol_state'](wx_parent=self.parent)
        else:
            uf_store['bmrb.thiol_state'](wx_parent=self.parent, state=state)


    def action_molecule_name(self, event):
        """Launch the molecule.name user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # Launch the dialog.
        uf_store['molecule.name'](wx_parent=self.parent, mol_id=id)


    def action_molecule_type(self, event):
        """Launch the molecule.type user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current type.
        type = None
        mol = return_molecule(id)
        if hasattr(mol, 'type') and mol.type != None:
            type = mol.type

        # Launch the dialog.
        if type == None:
            uf_store['molecule.type'](wx_parent=self.parent, mol_id=id)
        else:
            uf_store['molecule.type'](wx_parent=self.parent, mol_id=id, type=type)


    def is_complete(self):
        """Determine if the data input is complete.

        @return:    The answer to the question.
        @rtype:     bool
        """

        # Loop over the molecules.
        for mol in molecule_loop():
            # No name.
            if mol.name == None:
                return False

            # No molecule type.
            if not hasattr(mol, 'type') or mol.type == None:
                return False

            # No thiol state.
            if not hasattr(cdp, 'exp_info') or not hasattr(cdp.exp_info, 'thiol_state'):
                return False

        # Data input is complete.
        return True


    def set_box_label(self):
        """Set the label of the StaticBox."""

        # Determine if the data input is complete.
        label = self.title
        if self.is_complete():
            label += " (complete)"
        else:
            label += " (incomplete)"

        # Set the label.
        self.data_box.SetLabel(label)


    def setup(self):
        """Override the base variables."""

        # GUI variables.
        self.title = "Molecule information"
        self.observer_base_name = "molecule"
        self.button_placement = None

        # The column titles.
        self.columns = [
            "ID string",
            "Name",
            "Type",
            "Thiol state"
        ]

        # The right click popup menu.
        self.popup_menus = [
            {
                'id': wx.NewId(),
                'text': "&Name the molecule",
                'icon': fetch_icon(uf_info.get_uf('molecule.name').gui_icon),
                'method': self.action_molecule_name
            }, {
                'id': wx.NewId(),
                'text': "Set the molecule &type",
                'icon': fetch_icon(uf_info.get_uf('molecule.type').gui_icon),
                'method': self.action_molecule_type
            }, {
                'id': wx.NewId(),
                'text': "Set the thiol &state",
                'icon': fetch_icon(uf_info.get_uf('bmrb.thiol_state').gui_icon),
                'method': self.action_bmrb_thiol_state
            }
        ]


    def update_data(self):
        """Method called from self.build_element_safe() to update the list data."""

        # Expand the number of rows to match the number of molecules, and add the data.
        i = 0
        for mol, mol_id in molecule_loop(return_id=True):
            # Set the index.
            self.element.InsertStringItem(i, str_to_gui(mol_id))

            # Set the molecule name.
            if mol.name != None:
                self.element.SetStringItem(i, 1, str_to_gui(mol.name))

            # Set the molecule type.
            if hasattr(mol, 'type'):
                self.element.SetStringItem(i, 2, str_to_gui(mol.type))

            # Set the thiol state.
            if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'thiol_state'):
                self.element.SetStringItem(i, 3, str_to_gui(cdp.exp_info.thiol_state))

            # Increment the counter.
            i += 1
