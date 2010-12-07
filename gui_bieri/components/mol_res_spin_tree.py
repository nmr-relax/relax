###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
from generic_fns.pipes import get_pipe

# GUI module imports.
from gui_bieri import paths


class Mol_res_spin_tree(wx.Panel):
    """The tree view class."""

    def __init__(self, parent=None, id=None):
        """Set up the tree GUI element.

        @keyword parent:    The parent GUI element that this is to be attached to.
        @type parent:       wx object
        """

        # Execute the base class method.
        wx.Panel.__init__(self, parent, id, style=wx.WANTS_CHARS)

        # Some default values.
        self.icon_size = 22

        # The tree.
        self.tree = wx.TreeCtrl(parent=self, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE)

        # Resize the tree element.
        self.Bind(wx.EVT_SIZE, self._resize)

        # The tree roots.
        self.root = self.tree.AddRoot("Spin system information")
        self.tree.SetPyData(self.root, None)

        # Build the icon list.
        icon_list = wx.ImageList(self.icon_size, self.icon_size)
        self.icon_mol_index = icon_list.Add(wx.Bitmap(paths.MOLECULE_ICON, wx.BITMAP_TYPE_ANY))
        self.tree.SetImageList(icon_list)

        # Some weird black magic (this is essential)!!
        self.icon_list = icon_list

        # Populate the tree.
        self._tree_update()


    def _resize(self, event):
        """Resize the tree element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The panel dimensions.
        width, height = self.GetClientSizeTuple()

        # Set the tree dimensions.
        self.tree.SetDimensions(0, 0, width, height)


    def _tree_update(self, pipe_name=None):
        """Update the tree view using the given data pipe."""

        # The data pipe.
        if not pipe_name:
            pipe = cdp
        else:
            pipe = get_pipe(pipe_name)

        # No data pipe, so do nothing.
        if not pipe:
            return

        # The molecules.
        for mol in pipe.mol:
            # Append a molecule with name to the tree.
            mol_branch = self.tree.AppendItem(self.root, "Molecule %s" % mol.name)
            self.tree.SetPyData(mol_branch, None)

            # Set the bitmap.
            self.tree.SetItemImage(mol_branch, self.icon_mol_index, wx.TreeItemIcon_Normal & wx.TreeItemIcon_Expanded)

            # The residues.
            for res in mol.res:
                # Append a residue with name and number to the tree.
                res_branch = self.tree.AppendItem(mol_branch, "Residue %s %s" % (res.num, res.name))
                self.tree.SetPyData(res_branch, None)

                # The spins.
                for spin in res.spin:
                    # Append a spin with name and number to the tree.
                    spin_branch = self.tree.AppendItem(res_branch, "Spin %s %s" % (spin.num, spin.name))
                    self.tree.SetPyData(spin_branch, None)

            # Expand the molecule view.
            self.tree.Expand(mol_branch)

        # Expand the root.
        self.tree.Expand(self.root)



class Tree_window(wx.Frame):
    """A window element for the tree view."""

    def __init__(self, *args, **kwds):
        """Set up the relax prompt."""

        # Store the parent object.
        self.gui = kwds.pop('parent')

        # Create GUI elements
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        # Some default values.
        self.size_x = 500
        self.size_y = 1000
        self.border = 0

        # Set up the window.
        sizer = self.setup_window()

        # Add the tree view panel.
        self.tree_panel = Mol_res_spin_tree(parent=self, id=-1)
        sizer.Add(self.tree_panel, 1, wx.EXPAND|wx.ALL, self.border)


    def Show(self, show=True):
        """Change the behaviour of showing the window to update the content.

        @keyword show:  A flag which is True shows the window.
        @type show:     bool
        """

        # First update.
        self.tree_panel._tree_update()

        # Then show the window using the baseclass method.
        wx.Frame.Show(self, show)


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

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
