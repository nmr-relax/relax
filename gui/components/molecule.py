###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Michael Bieri                                       #
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
"""Module containing the classes for GUI components involving molecules."""

# Python module imports.
import wx
import wx.lib.buttons

# relax module imports.
from generic_fns.mol_res_spin import count_molecules, molecule_loop, return_molecule

from graphics import fetch_icon
from status import Status; status = Status()
from user_functions.data import Uf_info; uf_info = Uf_info()

# relax GUI module imports.
from gui.components.menu import build_menu_item
from gui.fonts import font
from gui.misc import add_border
from gui.string_conv import gui_to_str, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()


class Molecule:
    """The GUI element for listing loaded molecules."""

    # Some IDs for the menu entries.
    MENU_BMRB_THIOL_STATE = wx.NewId()
    MENU_MOLECULE_NAME = wx.NewId()
    MENU_MOLECULE_TYPE = wx.NewId()


    def __init__(self, parent=None, box=None, id=None, stretch=False):
        """Build the molecule list GUI element.

        @keyword parent:    The parent GUI element that this is to be attached to (the panel object).
        @type parent:       wx object
        @keyword data:      The data storage container.
        @type data:         class instance
        @keyword box:       The vertical box sizer to pack this GUI component into.
        @type box:          wx.BoxSizer instance
        @keyword id:        A unique identification string.  This is used to register the update method with the GUI user function observer object.
        @type id:           str
        @keyword stretch:   A flag which if True will allow the static box to stretch with the window.
        @type stretch:      bool
        """

        # Store the arguments.
        self.parent = parent
        self.stretch = stretch

        # Stretching.
        self.proportion = 0
        if stretch:
            self.proportion = 1

        # GUI variables.
        self.spacing = 5
        self.border = 5

        # First create a panel.
        self.panel = wx.Panel(self.parent)
        box.Add(self.panel, self.proportion, wx.ALL|wx.EXPAND, 0)

        # Add a sizer to the panel.
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(panel_sizer)

        # A static box to hold all the widgets, and its sizer.
        self.data_box = wx.StaticBox(self.panel, -1)
        self.set_box_label()
        self.data_box.SetFont(font.subtitle)
        sub_sizer = wx.StaticBoxSizer(self.data_box, wx.VERTICAL)

        # Add the sizer to the static box and the static box to the main box.
        panel_sizer.Add(sub_sizer, self.proportion, wx.ALL|wx.EXPAND, 0)

        # Add a border.
        box_centre = add_border(sub_sizer, border=self.border)

        # Initialise the element.
        box_centre.AddSpacer(self.spacing)
        self.init_element(box_centre)

        # Build the element.
        self.build_element()

        # Initialise observer name.
        self.name = 'molecule: %s' % id

        # Register the element for updating when a user function completes.
        self.observer_register()


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


    def build_element(self):
        """Build the molecule listing grid."""

        # Execution lock, so do nothing.
        if status.exec_lock.locked():
            return

        # Build the GUI element in a thread safe way.
        wx.CallAfter(self.build_element_safe)


    def build_element_safe(self):
        """Build the spectra listing GUI element in a thread safe wx.CallAfter call."""

        # First freeze the element, so that the GUI element doesn't update until the end.
        self.element.Freeze()

        # Update the label.
        self.set_box_label()

        # Delete the previous data.
        self.element.DeleteAllItems()

        # Expand the number of rows to match the number of molecules, and add the data.
        n = count_molecules()
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

        # Size the columns.
        self.size_cols()

        # Post a size event to get the scroll panel to update correctly.
        event = wx.PyCommandEvent(wx.EVT_SIZE.typeId, self.parent.GetId())
        wx.PostEvent(self.parent.GetEventHandler(), event)

        # Set the minimum height.
        if not self.stretch:
            head = self.height_char + 10
            centre = (self.height_char + 6) * n 
            foot = wx.SystemSettings_GetMetric(wx.SYS_HSCROLL_Y)
            height = head + centre + foot
            self.element.SetMinSize((-1, height))
            self.element.Layout()

        # Unfreeze.
        self.element.Thaw()


    def init_element(self, sizer):
        """Initialise the GUI element for the molecule listing.

        @param sizer:   The sizer element to pack the element into.
        @type sizer:    wx.BoxSizer instance
        """

        # List of molecules.
        self.element = wx.ListCtrl(self.panel, -1, style=wx.BORDER_SUNKEN|wx.LC_REPORT)

        # Initialise to 4 columns.
        self.element.InsertColumn(0, str_to_gui("ID string"))
        self.element.InsertColumn(1, str_to_gui("Name"))
        self.element.InsertColumn(2, str_to_gui("Type"))
        self.element.InsertColumn(3, str_to_gui("Thiol state"))

        # Properties.
        self.element.SetFont(font.normal)

        # Store the base heights.
        self.height_char = self.element.GetCharHeight()

        # Bind some events.
        self.element.Bind(wx.EVT_SIZE, self.resize)
        self.element.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.on_right_click)  # For wxMSW!
        self.element.Bind(wx.EVT_RIGHT_UP, self.on_right_click)   # For wxGTK!

        # Add list to sizer.
        sizer.Add(self.element, self.proportion, wx.ALL|wx.EXPAND, 0)


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


    def observer_register(self, remove=False):
        """Register and unregister methods with the observer objects.

        @keyword remove:    If set to True, then the methods will be unregistered.
        @type remove:       False
        """

        # Register.
        if not remove:
            status.observers.gui_uf.register(self.name, self.build_element)

        # Unregister.
        else:
            status.observers.gui_uf.unregister(self.name)


    def on_right_click(self, event):
        """Pop up menu for the right click.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execution lock, so do nothing.
        if status.exec_lock.locked():
            return

        # Initialise the menu.
        menu = wx.Menu()

        # Add some menu items for the spin user functions.
        menu.AppendItem(build_menu_item(menu, id=self.MENU_MOLECULE_NAME, text="&Name the molecule", icon=fetch_icon(uf_info.get_uf('molecule.name').gui_icon)))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_MOLECULE_TYPE, text="Set the molecule &type", icon=fetch_icon(uf_info.get_uf('molecule.type').gui_icon)))
        menu.AppendItem(build_menu_item(menu, id=self.MENU_BMRB_THIOL_STATE, text="Set the thiol &state", icon=fetch_icon(uf_info.get_uf('bmrb.thiol_state').gui_icon)))

        # Bind clicks.
        self.element.Bind(wx.EVT_MENU, self.action_molecule_name, id=self.MENU_MOLECULE_NAME)
        self.element.Bind(wx.EVT_MENU, self.action_molecule_type, id=self.MENU_MOLECULE_TYPE)
        self.element.Bind(wx.EVT_MENU, self.action_bmrb_thiol_state, id=self.MENU_BMRB_THIOL_STATE)

        # Pop up the menu.
        if status.show_gui:
            self.element.PopupMenu(menu)
            menu.Destroy()


    def resize(self, event):
        """Catch the resize to allow the element to be resized.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the column sizes.
        self.size_cols()

        # Continue with the normal resizing.
        event.Skip()


    def set_box_label(self):
        """Set the label of the StaticBox."""

        # Determine if the data input is complete.
        label = "Molecule information "
        if self.is_complete():
            label += "(complete)"
        else:
            label += "(incomplete)"

        # Set the label.
        self.data_box.SetLabel(label)


    def size_cols(self):
        """Set the column sizes."""

        # The element size.
        x, y = self.element.GetSize()

        # Number of columns.
        n = self.element.GetColumnCount()

        # Set to equal sizes.
        if n == 0:
            width = x
        else:
            width = int(x / n)

        # Set the column sizes.
        for i in range(n):
            self.element.SetColumnWidth(i, width)
