###############################################################################
#                                                                             #
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
"""The molecule, residue, and spin tree view GUI elements."""


# Python module imports.
import wx

# relax module imports.
from generic_fns.selection import is_mol_selected, is_res_selected, is_spin_selected
from generic_fns.mol_res_spin import get_molecule_ids, get_residue_ids, get_spin_ids, molecule_loop, residue_loop, spin_loop
from generic_fns.pipes import get_pipe
from status import Status; status = Status()

# relax GUI module imports.
from gui import paths
from gui.components.menu import build_menu_item
from gui.message import Question
from gui.misc import gui_to_str
from gui.uf_pages import User_functions


class Mol_res_spin_tree(wx.Window):
    """The tree view class."""

    # Some IDs for the menu entries.
    MENU_ROOT_MOLECULE_CREATE = wx.NewId()
    MENU_ROOT_LOAD_SPINS = wx.NewId()
    MENU_SPIN_SPIN_DELETE = wx.NewId()
    MENU_SPIN_SPIN_SELECT = wx.NewId()
    MENU_SPIN_SPIN_DESELECT = wx.NewId()
    MENU_RESIDUE_SPIN_ADD = wx.NewId()
    MENU_RESIDUE_RESIDUE_DELETE = wx.NewId()
    MENU_RESIDUE_RESIDUE_SELECT = wx.NewId()
    MENU_RESIDUE_RESIDUE_DESELECT = wx.NewId()
    MENU_MOLECULE_RESIDUE_CREATE = wx.NewId()
    MENU_MOLECULE_MOLECULE_DELETE = wx.NewId()
    MENU_MOLECULE_MOLECULE_DESELECT = wx.NewId()
    MENU_MOLECULE_MOLECULE_SELECT = wx.NewId()

    def __init__(self, gui, parent=None, id=None):
        """Set up the tree GUI element.

        @param gui:         The gui object.
        @type gui:          wx object
        @keyword parent:    The parent GUI element that this is to be attached to.
        @type parent:       wx object
        @keyword id:        The ID number.
        @type id:           int
        """

        # Store the args.
        self.gui = gui
        self.parent = parent

        # Execute the base class method.
        wx.Window.__init__(self, parent, id, style=wx.WANTS_CHARS)

        # Some default values.
        self.icon_size = 22

        # The tree.
        self.tree = wx.TreeCtrl(parent=self, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE)

        # A tracking structure for the tree IDs.
        self.tree_ids = {}

        # Resize the tree element.
        self.Bind(wx.EVT_SIZE, self._resize)

        # The tree roots.
        self.root = self.tree.AddRoot("Spin system information")
        self.tree.SetPyData(self.root, "root")

        # Build the icon list.
        icon_list = wx.ImageList(self.icon_size, self.icon_size)

        # The normal icons.
        self.icon_mol_index = icon_list.Add(wx.Bitmap(paths.icon_22x22.molecule, wx.BITMAP_TYPE_ANY))
        self.icon_mol_unfold_index = icon_list.Add(wx.Bitmap(paths.icon_22x22.molecule_unfolded, wx.BITMAP_TYPE_ANY))
        self.icon_res_index = icon_list.Add(wx.Bitmap(paths.icon_22x22.residue, wx.BITMAP_TYPE_ANY))
        self.icon_spin_index = icon_list.Add(wx.Bitmap(paths.icon_22x22.spin, wx.BITMAP_TYPE_ANY))

        # The deselected icons.
        self.icon_mol_index_desel = icon_list.Add(wx.Bitmap(paths.icon_22x22.molecule_grey, wx.BITMAP_TYPE_ANY))
        self.icon_mol_unfold_index_desel = icon_list.Add(wx.Bitmap(paths.icon_22x22.molecule_unfolded_grey, wx.BITMAP_TYPE_ANY))
        self.icon_res_index_desel = icon_list.Add(wx.Bitmap(paths.icon_22x22.residue_grey, wx.BITMAP_TYPE_ANY))
        self.icon_spin_index_desel = icon_list.Add(wx.Bitmap(paths.icon_22x22.spin_grey, wx.BITMAP_TYPE_ANY))

        # Set the icon list.
        self.tree.SetImageList(icon_list)

        # Some weird black magic (this is essential)!!
        self.icon_list = icon_list

        # Populate the tree.
        self.update()

        # Catch mouse events.
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self._selection)
        self.tree.Bind(wx.EVT_RIGHT_DOWN, self._right_click)


    def _resize(self, event):
        """Resize the tree element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The panel dimensions.
        width, height = self.GetClientSizeTuple()

        # Set the tree dimensions.
        self.tree.SetDimensions(0, 0, width, height)


    def _right_click(self, event):
        """Handle right clicks in the tree.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Obtain the position.
        pos = event.GetPosition()

        # Find the item clicked on.
        item, flags = self.tree.HitTest(pos)

        # The python data (with catch for wxPython 2.9 behaviour).
        if not item.IsOk():
            self.info = None
        else:
            self.info = self.tree.GetItemPyData(item)

        # Bring up the default menu.
        if self.info == None:
            self.menu_default()

        # Bring up the root menu.
        elif self.info == 'root':
            self.menu_root()

        # Bring up the molecule menu.
        elif self.info['type'] == 'mol':
            self.menu_molecule()

        # Bring up the residue menu.
        elif self.info['type'] == 'res':
            self.menu_residue()

        # Bring up the spin menu.
        elif self.info['type'] == 'spin':
            self.menu_spin()


    def _selection(self, event):
        """Handle changes in selection in the tree.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Find the item clicked on.
        item = event.GetItem()

        # The python data.
        info = self.tree.GetItemPyData(item)

        # Display the container.
        self.gui.spin_viewer.container.display(info)


    def create_molecule(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set up the user functions.
        user_functions = User_functions(self.gui.spin_viewer)

        # Call the dialog.
        user_functions.molecule.create()


    def create_residue(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set up the user functions.
        user_functions = User_functions(self.gui.spin_viewer)

        # Call the dialog.
        user_functions.residue.create(mol_name=self.info['mol_name'])


    def create_spin(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set up the user functions.
        user_functions = User_functions(self.gui.spin_viewer)

        # Call the dialog.
        user_functions.spin.create(mol_name=self.info['mol_name'], res_num=self.info['res_num'], res_name=self.info['res_name'])


    def delete_molecule(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to delete this molecule?  This only affects the spin data, all structural data will remain.  This operation cannot be undone."
        if status.show_gui and Question(msg, parent=self.gui.spin_viewer, default=False, size=(400, 170)).ShowModal() == wx.ID_NO:
            return

        # Delete the molecule.
        self.gui.interpreter.queue('molecule.delete', gui_to_str(self.info['id']))

        # Notify all observers that a user function has completed.
        status.observers.gui_uf.notify()


    def delete_residue(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to delete this residue?  This only affects the spin data, all structural data will remain.  This operation cannot be undone."
        if status.show_gui and Question(msg, parent=self.gui.spin_viewer, default=False, size=(400, 170)).ShowModal() == wx.ID_NO:
            return

        # Delete the residue.
        self.gui.interpreter.queue('residue.delete', gui_to_str(self.info['id']))

        # Notify all observers that a user function has completed.
        status.observers.gui_uf.notify()


    def delete_spin(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to delete this spin?  This only affects the spin data, all structural data will remain.  This operation cannot be undone."
        if status.show_gui and Question(msg, parent=self.gui.spin_viewer, default=False, size=(400, 170)).ShowModal() == wx.ID_NO:
            return

        # Delete the spin.
        self.gui.interpreter.queue('spin.delete', gui_to_str(self.info['id']))

        # Notify all observers that a user function has completed.
        status.observers.gui_uf.notify()


    def deselect_molecule(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to deselect all spins of this molecule?"
        if status.show_gui and Question(msg, parent=self.gui.spin_viewer, default=False).ShowModal() == wx.ID_NO:
            return

        # Deselect the molecule.
        self.gui.interpreter.queue('deselect.spin', spin_id=gui_to_str(self.info['id']), change_all=False)

        # Notify all observers that a user function has completed.
        status.observers.gui_uf.notify()


    def deselect_residue(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to deselect all spins of this residue?"
        if status.show_gui and Question(msg, parent=self.gui.spin_viewer, default=False).ShowModal() == wx.ID_NO:
            return

        # Deselect the residue.
        self.gui.interpreter.queue('deselect.spin', spin_id=gui_to_str(self.info['id']), change_all=False)

        # Notify all observers that a user function has completed.
        status.observers.gui_uf.notify()


    def deselect_spin(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Deselect the spin.
        self.gui.interpreter.queue('deselect.spin', spin_id=gui_to_str(self.info['id']), change_all=False)

        # Notify all observers that a user function has completed.
        status.observers.gui_uf.notify()


    def get_info(self):
        """Get the python data structure associated with the current item.

        @return:    The dictionary of data.
        @rtype:     dict
        """

        # The current item.
        item = self.tree.GetSelection()

        # No data.
        if not item.IsOk():
            return

        # Return the associated python data.
        return self.tree.GetItemPyData(item)


    def menu_default(self):
        """The right click root menu."""

        # The menu.
        menu = wx.Menu()

        # The load spins entry.
        item = build_menu_item(menu, id=self.MENU_ROOT_LOAD_SPINS, text="Load spins", icon=paths.icon_16x16.spin)
        menu.AppendItem(item)
        if status.exec_lock.locked():
            item.Enable(False)

        # The menu actions.
        self.Bind(wx.EVT_MENU, self.gui.spin_viewer.load_spins_wizard, id=self.MENU_ROOT_LOAD_SPINS)

        # Show the menu.
        if status.show_gui:
            self.PopupMenu(menu)
            menu.Destroy()


    def menu_molecule(self):
        """The right click molecule menu."""

        # The menu.
        menu = wx.Menu()
        item = build_menu_item(menu, id=self.MENU_MOLECULE_RESIDUE_CREATE, text="Add residue", icon=paths.icon_16x16.add)
        menu.AppendItem(item)
        if status.exec_lock.locked():
            item.Enable(False)
        item = build_menu_item(menu, id=self.MENU_MOLECULE_MOLECULE_DELETE, text="Delete molecule", icon=paths.icon_16x16.remove)
        menu.AppendItem(item)
        if status.exec_lock.locked():
            item.Enable(False)

        # Selection or deselection.
        if self.info['select']:
            item = build_menu_item(menu, id=self.MENU_MOLECULE_MOLECULE_DESELECT, text="Deselect")
            menu.AppendItem(item)
            if status.exec_lock.locked():
                item.Enable(False)
        else:
            item = build_menu_item(menu, id=self.MENU_MOLECULE_MOLECULE_SELECT, text="Select")
            menu.AppendItem(item)
            if status.exec_lock.locked():
                item.Enable(False)

        # The menu actions.
        self.Bind(wx.EVT_MENU, self.create_residue, id=self.MENU_MOLECULE_RESIDUE_CREATE)
        self.Bind(wx.EVT_MENU, self.delete_molecule, id=self.MENU_MOLECULE_MOLECULE_DELETE)
        if self.info['select']:
            self.Bind(wx.EVT_MENU, self.deselect_molecule, id=self.MENU_MOLECULE_MOLECULE_DESELECT)
        else:
            self.Bind(wx.EVT_MENU, self.select_molecule, id=self.MENU_MOLECULE_MOLECULE_SELECT)

        # Show the menu.
        if status.show_gui:
            self.PopupMenu(menu)
            menu.Destroy()


    def menu_residue(self):
        """The right click molecule menu."""

        # The menu.
        menu = wx.Menu()
        item = build_menu_item(menu, id=self.MENU_RESIDUE_SPIN_ADD, text="Add spin", icon=paths.icon_16x16.add)
        menu.AppendItem(item)
        if status.exec_lock.locked():
            item.Enable(False)
        item = build_menu_item(menu, id=self.MENU_RESIDUE_RESIDUE_DELETE, text="Delete residue", icon=paths.icon_16x16.remove)
        menu.AppendItem(item)
        if status.exec_lock.locked():
            item.Enable(False)

        # Selection or deselection.
        if self.info['select']:
            item = build_menu_item(menu, id=self.MENU_RESIDUE_RESIDUE_DESELECT, text="Deselect")
            menu.AppendItem(item)
            if status.exec_lock.locked():
                item.Enable(False)
        else:
            item = build_menu_item(menu, id=self.MENU_RESIDUE_RESIDUE_SELECT, text="Select")
            menu.AppendItem(item)
            if status.exec_lock.locked():
                item.Enable(False)

        # The menu actions.
        self.Bind(wx.EVT_MENU, self.create_spin, id=self.MENU_RESIDUE_SPIN_ADD)
        self.Bind(wx.EVT_MENU, self.delete_residue, id=self.MENU_RESIDUE_RESIDUE_DELETE)
        if self.info['select']:
            self.Bind(wx.EVT_MENU, self.deselect_residue, id=self.MENU_RESIDUE_RESIDUE_DESELECT)
        else:
            self.Bind(wx.EVT_MENU, self.select_residue, id=self.MENU_RESIDUE_RESIDUE_SELECT)

        # Show the menu.
        if status.show_gui:
            self.PopupMenu(menu)
            menu.Destroy()


    def menu_root(self):
        """The right click root menu."""

        # The menu.
        menu = wx.Menu()

        # The add molecule entry.
        item = build_menu_item(menu, id=self.MENU_ROOT_MOLECULE_CREATE, text="Add molecule", icon=paths.icon_16x16.add)
        menu.AppendItem(item)
        if status.exec_lock.locked():
            item.Enable(False)

        # The add molecule entry.
        item = build_menu_item(menu, id=self.MENU_ROOT_LOAD_SPINS, text="Load spins", icon=paths.icon_16x16.spin)
        menu.AppendItem(item)
        if status.exec_lock.locked():
            item.Enable(False)

        # The menu actions.
        self.Bind(wx.EVT_MENU, self.create_molecule, id=self.MENU_ROOT_MOLECULE_CREATE)
        self.Bind(wx.EVT_MENU, self.gui.spin_viewer.load_spins_wizard, id=self.MENU_ROOT_LOAD_SPINS)

        # Show the menu.
        if status.show_gui:
            self.PopupMenu(menu)
            menu.Destroy()


    def menu_spin(self):
        """The right click spin menu."""

        # The menu.
        menu = wx.Menu()
        item = build_menu_item(menu, id=self.MENU_SPIN_SPIN_DELETE, text="Delete spin", icon=paths.icon_16x16.remove)
        menu.AppendItem(item)
        if status.exec_lock.locked():
            item.Enable(False)

        # Selection or deselection.
        if self.info['select']:
            item = build_menu_item(menu, id=self.MENU_SPIN_SPIN_DESELECT, text="Deselect")
            menu.AppendItem(item)
            if status.exec_lock.locked():
                item.Enable(False)
        else:
            item = build_menu_item(menu, id=self.MENU_SPIN_SPIN_SELECT, text="Select")
            menu.AppendItem(item)
            if status.exec_lock.locked():
                item.Enable(False)

        # The menu actions.
        self.Bind(wx.EVT_MENU, self.delete_spin, id=self.MENU_SPIN_SPIN_DELETE)
        if self.info['select']:
            self.Bind(wx.EVT_MENU, self.deselect_spin, id=self.MENU_SPIN_SPIN_DESELECT)
        else:
            self.Bind(wx.EVT_MENU, self.select_spin, id=self.MENU_SPIN_SPIN_SELECT)

        # Show the menu.
        if status.show_gui:
            self.PopupMenu(menu)
            menu.Destroy()


    def prune_mol(self):
        """Remove any molecules which have been deleted."""

        # Get a list of molecule IDs from the relax data store.
        mol_ids = get_molecule_ids()

        # Find if the molecule has been removed.
        prune_list = []
        for key in self.tree_ids.keys():
            # Get the python data.
            info = self.tree.GetItemPyData(key)

            # Prune if it has been removed.
            if info['id'] not in mol_ids:
                self.tree.Delete(key)
                self.tree_ids.pop(key)


    def prune_res(self, mol_branch_id, mol_id):
        """Remove any molecules which have been deleted.

        @param mol_branch_id:   The molecule branch ID of the wx.TreeCtrl object.
        @type mol_branch_id:    TreeItemId
        @param mol_id:          The molecule identification string.
        @type mol_id:           str
        """

        # Get a list of residue IDs from the relax data store.
        res_ids = get_residue_ids(mol_id)

        # Find if the molecule has been removed.
        prune_list = []
        for key in self.tree_ids[mol_branch_id].keys():
            # Get the python data.
            info = self.tree.GetItemPyData(key)

            # Prune if it has been removed.
            if info['id'] not in res_ids:
                self.tree.Delete(key)
                self.tree_ids[mol_branch_id].pop(key)


    def prune_spin(self, mol_branch_id, res_branch_id, res_id):
        """Remove any spins which have been deleted.

        @param mol_branch_id:   The molecule branch ID of the wx.TreeCtrl object.
        @type mol_branch_id:    TreeItemId
        @param res_branch_id:   The residue branch ID of the wx.TreeCtrl object.
        @type res_branch_id:    TreeItemId
        @param res_id:          The residue identification string.
        @type res_id:           str
        """

        # Get a list of spin IDs from the relax data store.
        spin_ids = get_spin_ids(res_id)

        # Find if the molecule has been removed.
        prune_list = []
        for key in self.tree_ids[mol_branch_id][res_branch_id].keys():
            # Get the python data.
            info = self.tree.GetItemPyData(key)

            # Prune if it has been removed.
            if info['id'] not in spin_ids:
                self.tree.Delete(key)
                self.tree_ids[mol_branch_id][res_branch_id].pop(key)


    def select_molecule(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to select all spins of this molecule?"
        if status.show_gui and Question(msg, parent=self.gui.spin_viewer, default=False).ShowModal() == wx.ID_NO:
            return

        # Select the molecule.
        self.gui.interpreter.queue('select.spin', spin_id=gui_to_str(self.info['id']), change_all=False)

        # Notify all observers that a user function has completed.
        status.observers.gui_uf.notify()


    def select_residue(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to select all spins of this residue?"
        if status.show_gui and Question(msg, parent=self.gui.spin_viewer, default=False).ShowModal() == wx.ID_NO:
            return

        # Select the residue.
        self.gui.interpreter.queue('select.spin', spin_id=gui_to_str(self.info['id']), change_all=False)

        # Notify all observers that a user function has completed.
        status.observers.gui_uf.notify()


    def select_spin(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Select the spin.
        self.gui.interpreter.queue('select.spin', spin_id=gui_to_str(self.info['id']), change_all=False)

        # Notify all observers that a user function has completed.
        status.observers.gui_uf.notify()


    def set_bitmap_mol(self, mol_branch_id, select=True):
        """Set the molecule bitmaps.

        @param mol_branch_id:   The molecule branch ID of the wx.TreeCtrl object.
        @type mol_branch_id:    TreeItemId
        @keyword select:        The selection flag.
        @type select:           bool
        """

        # The bitmaps for the selected state.
        if select:
            bmp = self.icon_mol_index
            bmp_unfold = self.icon_mol_unfold_index

        # The bitmaps for the deselected state.
        else:
            bmp = self.icon_mol_index_desel
            bmp_unfold = self.icon_mol_unfold_index_desel

        # Set the image.
        self.tree.SetItemImage(mol_branch_id, bmp, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(mol_branch_id, bmp_unfold, wx.TreeItemIcon_Expanded)


    def set_bitmap_res(self, res_branch_id, select=True):
        """Set the residue bitmaps.

        @param res_branch_id:   The residue branch ID of the wx.TreeCtrl object.
        @type res_branch_id:    TreeItemId
        @keyword select:        The selection flag.
        @type select:           bool
        """

        # The bitmaps for the selected state.
        if select:
            bmp = self.icon_res_index

        # The bitmaps for the deselected state.
        else:
            bmp = self.icon_res_index_desel

        # Set the image.
        self.tree.SetItemImage(res_branch_id, bmp, wx.TreeItemIcon_Normal & wx.TreeItemIcon_Expanded)


    def set_bitmap_spin(self, spin_branch_id, select=True):
        """Set the spin bitmaps.

        @param spin_branch_id:  The spin branch ID of the wx.TreeCtrl object.
        @type spin_branch_id:   TreeItemId
        @keyword select:        The selection flag.
        @type select:           bool
        """

        # The bitmaps for the selected state.
        if select:
            bmp = self.icon_spin_index

        # The bitmaps for the deselected state.
        else:
            bmp = self.icon_spin_index_desel

        # Set the image.
        self.tree.SetItemImage(spin_branch_id, bmp, wx.TreeItemIcon_Normal & wx.TreeItemIcon_Expanded)


    def update(self, pipe_name=None):
        """Update the tree view using the given data pipe."""

        # Acquire the pipe and spin locks.
        status.pipe_lock.acquire('spin viewer window')
        status.spin_lock.acquire('spin viewer window')
        try:
            # The data pipe.
            if not pipe_name:
                pipe = cdp
            else:
                pipe = get_pipe(pipe_name)

            # No data pipe, so delete everything and return.
            if not pipe:
                self.tree.DeleteChildren(self.root)
                return

            # Update the molecules.
            for mol, mol_id in molecule_loop(return_id=True):
                self.update_mol(mol, mol_id)

            # Remove any deleted molecules.
            self.prune_mol()

        # Release the locks.
        finally:
            status.pipe_lock.release('spin viewer window')
            status.spin_lock.release('spin viewer window')


    def update_mol(self, mol, mol_id):
        """Update the given molecule in the tree.

        @param mol:     The molecule container.
        @type mol:      MoleculeContainer instance
        @param mol_id:  The molecule identification string.
        @type mol_id:   str
        """

        # Find the molecule, if it already exists.
        new_mol = True
        for key in self.tree_ids.keys():
            # Get the python data.
            data = self.tree.GetItemPyData(key)

            # Check the mol_id for a match and, if so, terminate to speed things up.
            if mol_id == data['id']:
                new_mol = False
                mol_branch_id = key
                break

        # A new molecule.
        if new_mol:
            # Append a molecule with name to the tree.
            mol_branch_id = self.tree.AppendItem(self.root, "Molecule: %s" % mol.name)

            # The data to store.
            data = {
                'type': 'mol',
                'mol_name': mol.name,
                'id': mol_id,
                'select': is_mol_selected(mol_id)
            }
            self.tree.SetPyData(mol_branch_id, data)

            # Add the id to the tracking structure.
            self.tree_ids[mol_branch_id] = {}

            # Set the bitmap.
            self.set_bitmap_mol(mol_branch_id, select=data['select'])

        # An old molecule.
        else:
            # Check the selection state.
            select = is_mol_selected(data['id'])

            # Change of state.
            if select != data['select']:
                # Store the new state.
                data['select'] = select

                # Set the bitmap.
                self.set_bitmap_mol(mol_branch_id, select=data['select'])

        # Update the residues of this molecule.
        for res, res_id in residue_loop(mol_id, return_id=True):
            self.update_res(mol_branch_id, mol, res, res_id)

        # Start new molecules expanded.
        if new_mol and data['select']:
            self.tree.Expand(mol_branch_id)

        # Remove any deleted residues.
        self.prune_res(mol_branch_id, mol_id)

        # Expand the root.
        self.tree.Expand(self.root)


    def update_res(self, mol_branch_id, mol, res, res_id):
        """Update the given residue in the tree.

        @param mol_branch_id:   The molecule branch ID of the wx.TreeCtrl object.
        @type mol_branch_id:    TreeItemId
        @param mol:             The molecule container.
        @type mol:              MoleculeContainer instance
        @param res:             The residue container.
        @type res:              ResidueContainer instance
        @param res_id:          The residue identification string.
        @type res_id:           str
        """

        # Find the residue, if it already exists.
        new_res = True
        for key in self.tree_ids[mol_branch_id].keys():
            # Get the python data.
            data = self.tree.GetItemPyData(key)

            # Check the res_id for a match and, if so, terminate to speed things up.
            if res_id == data['id']:
                new_res = False
                res_branch_id = key
                break

        # A new residue.
        if new_res:
            # Append a residue with name and number to the tree.
            res_branch_id = self.tree.AppendItem(mol_branch_id, "Residue: %s %s" % (res.num, res.name))

            # The data to store.
            data = {
                'type': 'res',
                'mol_name': mol.name,
                'res_name': res.name,
                'res_num': res.num,
                'id': res_id,
                'select': is_res_selected(res_id)
            }
            self.tree.SetPyData(res_branch_id, data)

            # Add the id to the tracking structure.
            self.tree_ids[mol_branch_id][res_branch_id] = {}

            # Set the bitmap.
            self.set_bitmap_res(res_branch_id, select=data['select'])

        # An old residue.
        else:
            # Check the selection state.
            select = is_res_selected(data['id'])

            # Change of state.
            if select != data['select']:
                # Store the new state.
                data['select'] = select

                # Set the bitmap.
                self.set_bitmap_res(res_branch_id, select=data['select'])

        # Update the spins of this residue.
        for spin, spin_id in spin_loop(res_id, return_id=True):
            self.update_spin(mol_branch_id, res_branch_id, mol, res, spin, spin_id)

        # Start new residues expanded.
        if new_res and data['select']:
            self.tree.Expand(res_branch_id)

        # Remove any deleted spins.
        self.prune_spin(mol_branch_id, res_branch_id, res_id)


    def update_spin(self, mol_branch_id, res_branch_id, mol, res, spin, spin_id):
        """Update the given spin in the tree.

        @param mol_branch_id:   The molecule branch ID of the wx.TreeCtrl object.
        @type mol_branch_id:    TreeItemId
        @param res_branch_id:   The residue branch ID of the wx.TreeCtrl object.
        @type res_branch_id:    TreeItemId
        @param mol:             The molecule container.
        @type mol:              MoleculeContainer instance
        @param res:             The residue container.
        @type res:              ResidueContainer instance
        @param spin:            The spin container.
        @type spin:             SpinContainer instance
        @param spin_id:         The spin identification string.
        @type spin_id:          str
        """

        # Find the spin, if it already exists.
        new_spin = True
        for key in self.tree_ids[mol_branch_id][res_branch_id].keys():
            # Get the python data.
            data = self.tree.GetItemPyData(key)

            # Check the spin_id for a match and, if so, terminate to speed things up.
            if spin_id == data['id']:
                new_spin = False
                spin_branch_id = key
                break

        # A new spin.
        if new_spin:
            # Append a spin with name and number to the tree.
            spin_branch_id = self.tree.AppendItem(res_branch_id, "Spin: %s %s" % (spin.num, spin.name))

            # The data to store.
            data = {
                'type': 'spin',
                'mol_name': mol.name,
                'res_name': res.name,
                'res_num': res.num,
                'spin_name': spin.name,
                'spin_num': spin.num,
                'id': spin_id,
                'select': is_spin_selected(spin_id)
            }
            self.tree.SetPyData(spin_branch_id, data)

            # Add the id to the tracking structure.
            self.tree_ids[mol_branch_id][res_branch_id][spin_branch_id] = True

            # Set the bitmap.
            self.set_bitmap_spin(spin_branch_id, select=data['select'])

        # An old spin.
        else:
            # Check the selection state.
            select = is_spin_selected(data['id'])

            # Change of state.
            if select != data['select']:
                # Store the new state.
                data['select'] = select

                # Set the bitmap.
                self.set_bitmap_spin(spin_branch_id, select=data['select'])

        # Start new spins expanded.
        if new_spin and data['select']:
            self.tree.Expand(spin_branch_id)
