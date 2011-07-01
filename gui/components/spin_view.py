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
"""The molecule, residue, and spin tree view GUI elements."""


# Python module imports.
from re import search
from string import replace, split
import wx

# relax module imports.
from generic_fns.mol_res_spin import get_molecule_ids, get_residue_ids, get_spin_ids, generate_spin_id, molecule_loop, residue_loop, return_spin, spin_loop
from generic_fns.pipes import cdp_name, get_pipe, pipe_names

# GUI module imports.
from gui import paths


class Container(wx.Window):
    """The molecule, residue, and spin container window."""

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

        # Some variables.
        self.border = 10

        # Execute the base class method.
        wx.Window.__init__(self, parent, id, style=wx.BORDER_SUNKEN)

        # Set a minimum size for the window.
        self.SetMinSize((500, 500))

        # Add a sizer.
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        # Display the root window.
        self.display_root()

        # Resizing.
        self.Bind(wx.EVT_SIZE, self._resize)


    def _resize(self, event):
        """Resize the tree element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Re-perform the window layout.
        self.Layout()
        self.Refresh()


    def create_head_text(self, text):
        """Generate the wx.StaticText object for header text.

        @param text:    The text of the subtitle.
        @type text:     str
        @return:        The subtitle object.
        @rtype:         wx.StaticText instance
        """

        # Unicode.
        text = unicode(text)

        # Fix for the '&' character.
        text = replace(text, '&', '&&')

        # The object.
        obj = wx.StaticText(self, -1, text)

        # Formatting.
        obj.SetFont(wx.Font(pointSize=12, family=wx.FONTFAMILY_ROMAN, style=wx.ITALIC, weight=wx.NORMAL, face='Times'))

        # Return the object.
        return obj


    def create_subtitle(self, text):
        """Generate the subtitle wx.StaticText object.

        @param text:    The text of the subtitle.
        @type text:     str
        @return:        The subtitle object.
        @rtype:         wx.StaticText instance
        """

        # Unicode.
        text = unicode(text)

        # Fix for the '&' character.
        text = replace(text, '&', '&&')

        # The object.
        obj = wx.StaticText(self, -1, text)

        # Formatting.
        obj.SetFont(wx.Font(pointSize=16, family=wx.FONTFAMILY_ROMAN, style=wx.ITALIC, weight=wx.NORMAL, face='Times'))

        # Return the object.
        return obj


    def create_title(self, text):
        """Generate the title wx.StaticText object.

        @param text:    The text of the subtitle.
        @type text:     str
        @return:        The subtitle object.
        @rtype:         wx.StaticText instance
        """

        # The object.
        title = wx.StaticText(self, -1, text)

        # Formatting.
        title.SetFont(wx.Font(pointSize=32, family=wx.FONTFAMILY_ROMAN, style=wx.ITALIC, weight=wx.NORMAL, face='Times'))

        # Return the object.
        return title


    def display(self, info):
        """Display the info for the selected container.

        @param info:    The information list consisting of the container type ('root', 'mol', 'res', or 'spin'), the molecule name, the residue number, the residue name, the spin number, and the spin name.  The name and number information is dropped when not needed.
        @type info:     list of str and int
        """

        # Destroy all the original contents.
        self.main_sizer.Clear(deleteWindows=True)

        # The root window display.
        if info == 'root':
            self.display_root()

        # The molecule container display.
        elif info[0] == 'mol':
            self.mol_container(info[1])

        # The residue container display.
        elif info[0] == 'res':
            self.res_container(info[1], info[2], info[3])

        # The spin container display.
        elif info[0] == 'spin':
            self.spin_container(info[1], info[2], info[3], info[4], info[5])

        # Re-perform the window layout.
        self.Layout()
        self.Refresh()


    def display_root(self):
        """Build and display the root window."""

        # A sizer for the header.
        sizer = wx.BoxSizer(wx.VERTICAL)

        # The title
        title = self.create_title("The spin view window")
        sizer.Add(title, 0, wx.LEFT, 0)

        # Add to the sizer.
        self.main_sizer.Add(sizer, 0, wx.ALL|wx.EXPAND, border=self.border)


    def mol_container(self, mol_name=None):
        """Build and display the molecule container

        @keyword mol_name:  The name of the molecule.
        @type mol_name:     str
        """

        # Store the args.
        self.mol_name = mol_name

        # The molecule ID.
        self.mol_id = generate_spin_id(mol_name=mol_name)

        # Create the header.
        sizer = self.mol_header()

        # Add to the sizer.
        self.main_sizer.Add(sizer, 0, wx.ALL|wx.EXPAND, border=self.border)

        # A divider.
        line = wx.StaticLine(self, -1, (25, 50))
        self.main_sizer.Add(line, 0, wx.EXPAND|wx.ALL, border=self.border)


    def mol_header(self):
        """Create the header for the molecule container.

        @return:    The sizer containing the header.
        @rtype:     wx.Sizer instance
        """

        # A sizer for the header.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # A sizer for the text component of the header.
        text_sizer = wx.BoxSizer(wx.VERTICAL)

        # The title
        title = self.create_title("Molecule container")
        text_sizer.Add(title, 0, wx.LEFT, 0)

        # Spacer.
        text_sizer.AddSpacer(30)

        # The info grid.
        grid_sizer = wx.FlexGridSizer(1, 2, 5, 50)
        grid_sizer.Add(self.create_head_text("Molecule:"), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text(self.mol_name), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text("Molecule ID string:"), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text("'%s'" % self.mol_id), 0, wx.ADJUST_MINSIZE, 0)
        text_sizer.Add(grid_sizer, 0, wx.LEFT, 0)

        # Add the text sizer to the main header sizer.
        sizer.Add(text_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Stretch spacer.
        sizer.AddStretchSpacer()

        # The graphic.
        image = wx.StaticBitmap(self, -1, wx.Bitmap(paths.WIZARD_IMAGE_PATH + 'molecule.png', wx.BITMAP_TYPE_ANY))
        sizer.Add(image, 0, wx.RIGHT, 0)

        # Return the sizer.
        return sizer


    def res_container(self, mol_name=None, res_num=None, res_name=None):
        """Build and display the residue container

        @keyword mol_name:  The molecule name.
        @type mol_name:     str
        @keyword res_num:   The residue number.
        @type res_num:      str
        @keyword res_name:  The residue name.
        @type res_name:     str
        """

        # Store the args.
        self.mol_name = mol_name
        self.res_num = res_num
        self.res_name = res_name

        # The residue ID.
        self.res_id = generate_spin_id(mol_name=mol_name, res_num=res_num, res_name=res_name)

        # Create the header.
        sizer = self.res_header()

        # Add to the main sizer.
        self.main_sizer.Add(sizer, 0, wx.ALL|wx.EXPAND, border=self.border)

        # A divider.
        line = wx.StaticLine(self, -1, (25, 50))
        self.main_sizer.Add(line, 0, wx.EXPAND|wx.ALL, border=self.border)


    def res_header(self):
        """Create the header for the residue container.

        @return:    The sizer containing the header.
        @rtype:     wx.Sizer instance
        """

        # A sizer for the header.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # A sizer for the text component of the header.
        text_sizer = wx.BoxSizer(wx.VERTICAL)

        # The title
        title = self.create_title("Residue container")
        text_sizer.Add(title, 0, wx.LEFT, 0)

        # Spacer.
        text_sizer.AddSpacer(30)

        # The info grid.
        grid_sizer = wx.FlexGridSizer(4, 2, 5, 50)
        grid_sizer.Add(self.create_head_text("Molecule:"), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text(self.mol_name), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text("Residue number:"), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text(self.res_num), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text("Residue name:"), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text(self.res_name), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text("Residue ID string:"), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text("'%s'" % self.res_id), 0, wx.ADJUST_MINSIZE, 0)
        text_sizer.Add(grid_sizer, 0, wx.LEFT, 0)

        # Add the text sizer to the main header sizer.
        sizer.Add(text_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Stretch spacer.
        sizer.AddStretchSpacer()

        # The graphic.
        image = wx.StaticBitmap(self, -1, wx.Bitmap(paths.WIZARD_IMAGE_PATH + 'residue.png', wx.BITMAP_TYPE_ANY))
        sizer.Add(image, 0, wx.RIGHT, 0)

        # Return the sizer.
        return sizer


    def spin_container(self, mol_name=None, res_num=None, res_name=None, spin_num=None, spin_name=None):
        """Build and display the spin container

        @keyword mol_name:  The molecule name.
        @type mol_name:     str
        @keyword res_num:   The residue number.
        @type res_num:      str
        @keyword res_name:  The residue name.
        @type res_name:     str
        @keyword spin_num:   The spin number.
        @type spin_num:      str
        @keyword spin_name:  The spin name.
        @type spin_name:     str
        """

        # Store the args.
        self.mol_name = mol_name
        self.res_num = res_num
        self.res_name = res_name
        self.spin_num = spin_num
        self.spin_name = spin_name

        # The spin ID.
        self.spin_id = generate_spin_id(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin_num, spin_name=spin_name)

        # Create the header.
        sizer = self.spin_header()

        # Add to the main sizer.
        self.main_sizer.Add(sizer, 0, wx.ALL|wx.EXPAND, border=self.border)

        # A divider.
        line = wx.StaticLine(self, -1, (25, 50))
        self.main_sizer.Add(line, 0, wx.EXPAND|wx.ALL, border=self.border)

        # The spin container variables.
        sizer2 = self.spin_vars()
        self.main_sizer.Add(sizer2, 1, wx.ALL|wx.EXPAND, border=self.border)


    def spin_header(self):
        """Create the header for the spin container.

        @return:    The sizer containing the header.
        @rtype:     wx.Sizer instance
        """

        # A sizer for the header.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # A sizer for the text component of the header.
        text_sizer = wx.BoxSizer(wx.VERTICAL)

        # The title
        title = self.create_title("Spin container")
        text_sizer.Add(title, 0, wx.LEFT, 0)

        # Spacer.
        text_sizer.AddSpacer(30)

        # The info grid.
        grid_sizer = wx.FlexGridSizer(6, 2, 5, 50)
        grid_sizer.Add(self.create_head_text("Molecule:"), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text(self.mol_name), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text("Residue number:"), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text(self.res_num), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text("Residue name:"), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text(self.res_name), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text("Spin number:"), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text(self.spin_num), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text("Spin name:"), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text(self.spin_name), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text("Spin ID string:"), 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer.Add(self.create_head_text("'%s'" % self.spin_id), 0, wx.ADJUST_MINSIZE, 0)
        text_sizer.Add(grid_sizer, 0, wx.LEFT, 0)

        # Add the text sizer to the main header sizer.
        sizer.Add(text_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Stretch spacer.
        sizer.AddStretchSpacer()

        # The graphic.
        image = wx.StaticBitmap(self, -1, wx.Bitmap(paths.WIZARD_IMAGE_PATH + 'spin.png', wx.BITMAP_TYPE_ANY))
        sizer.Add(image, 0, wx.RIGHT, 0)

        # Return the sizer.
        return sizer


    def spin_vars(self, blacklist=[]):
        """Create the variable table for the spin container.

        @keyword blacklist: A list of spin container objects to blacklist from the variable display table.
        @type blacklist:    list of str
        @return:            The sizer containing the table.
        @rtype:             wx.Sizer instance
        """

        # A sizer for the table.
        sizer = wx.BoxSizer(wx.VERTICAL)

        # The title
        title = self.create_subtitle("Spin container contents")
        sizer.Add(title, 0, wx.LEFT, 0)

        # Add a spacer.
        sizer.AddSpacer(20)

        # The table.
        table = wx.ListCtrl(self, -1, style=wx.BORDER_SUNKEN|wx.LC_REPORT)

        # The headers.
        table.InsertColumn(0, "Variable")
        table.InsertColumn(1, "Value")
        table.InsertColumn(2, "Type")

        # The widths.
        table.SetColumnWidth(0, 300)
        table.SetColumnWidth(1, 200)
        table.SetColumnWidth(2, 200)

        # The spin container.
        spin = return_spin(self.spin_id)

        # Add some names to the blacklist.
        blacklist += ['is_empty']

        # Loop over the contents of the spin container.
        for name in dir(spin):
            # Skip special objects.
            if search('^_', name):
                continue

            # Blacklisted names.
            if name in blacklist:
                continue

            # Get the object.
            obj = getattr(spin, name)

            # The type.
            obj_type = split(str(type(obj)), "'")[1]

            # List types.
            if obj_type in ['list', 'numpy.ndarray'] and len(obj) > 1:
                # The first row.
                table.Append((name, "[%s," % obj[0], obj_type))

                # The rest of the rows.
                for i in range(1, len(obj)-1):
                    table.Append(('', " %s," % obj[i], ''))

                # The last row.
                table.Append(('', " %s]" % obj[-1], ''))

            # Dictionary types.
            elif obj_type == 'dict':
                # The keys.
                keys = obj.keys()
                keys.sort()

                # Single entry (or None).
                if len(keys) < 2:
                    table.Append((name, obj, obj_type))
                    continue

                # The first row.
                table.Append((name, "{'%s': %s," % (keys[0], obj[keys[0]]), obj_type))

                # The rest of the rows.
                for i in range(1, len(keys)-1):
                    table.Append(('', " '%s': %s," % (keys[i], obj[keys[i]]), ''))

                # The last row.
                table.Append(('', " '%s': %s}" % (keys[-1], obj[keys[-1]]), ''))

            # All other data types.
            else:
                table.Append((name, obj, obj_type))

        # Add the table to the sizer.
        sizer.Add(table, 1, wx.ALL|wx.EXPAND, 0)

        # Return the sizer.
        return sizer



class Mol_res_spin_tree(wx.Window):
    """The tree view class."""

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
        self.icon_mol_index = icon_list.Add(wx.Bitmap(paths.icon_22x22.molecule, wx.BITMAP_TYPE_ANY))
        self.icon_mol_unfold_index = icon_list.Add(wx.Bitmap(paths.icon_22x22.molecule_unfolded, wx.BITMAP_TYPE_ANY))
        self.icon_res_index = icon_list.Add(wx.Bitmap(paths.icon_22x22.residue, wx.BITMAP_TYPE_ANY))
        self.icon_spin_index = icon_list.Add(wx.Bitmap(paths.icon_22x22.spin, wx.BITMAP_TYPE_ANY))
        self.tree.SetImageList(icon_list)

        # Some weird black magic (this is essential)!!
        self.icon_list = icon_list

        # Populate the tree.
        self.update()

        # Catch mouse events.
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self._selection)
        self.tree.Bind(wx.EVT_RIGHT_DOWN, self._right_click)


    def _mol_menu(self):
        """The right click molecule menu."""

        # Some ids.
        ids = []
        for i in range(2):
            ids.append(wx.NewId())

        # The menu.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[0], text="Add residue", icon=paths.icon_16x16.add))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[1], text="Delete molecule", icon=paths.icon_16x16.remove))

        # The menu actions.
        self.Bind(wx.EVT_MENU, self.residue_create, id=ids[0])
        self.Bind(wx.EVT_MENU, self.molecule_delete, id=ids[1])

        # Show the menu.
        self.PopupMenu(menu)
        menu.Destroy()


    def _res_menu(self):
        """The right click molecule menu."""

        # Some ids.
        ids = []
        for i in range(2):
            ids.append(wx.NewId())

        # The menu.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[0], text="Add spin", icon=paths.icon_16x16.add))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[1], text="Delete residue", icon=paths.icon_16x16.remove))

        # The menu actions.
        self.Bind(wx.EVT_MENU, self.spin_create, id=ids[0])
        self.Bind(wx.EVT_MENU, self.residue_delete, id=ids[1])

        # Show the menu.
        self.PopupMenu(menu)
        menu.Destroy()


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

        # The python data.
        self.info = self.tree.GetItemPyData(item)

        # Bring up the root menu.
        if self.info == 'root':
            self._root_menu()

        # Bring up the molecule menu.
        elif self.info[0] == 'mol':
            self._mol_menu()

        # Bring up the residue menu.
        elif self.info[0] == 'res':
            self._res_menu()

        # Bring up the spin menu.
        elif self.info[0] == 'spin':
            self._spin_menu()


    def _root_menu(self):
        """The right click root menu."""

        # Some ids.
        ids = []
        for i in range(1):
            ids.append(wx.NewId())

        # The menu.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[0], text="Add molecule", icon=paths.icon_16x16.add))

        # The menu actions.
        self.Bind(wx.EVT_MENU, self.gui.user_functions.molecule.create, id=ids[0])

        # Show the menu.
        self.PopupMenu(menu)
        menu.Destroy()


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
        self.gui.spin_view.container.display(info)


    def _spin_menu(self):
        """The right click spin menu."""

        # Some ids.
        ids = []
        for i in range(1):
            ids.append(wx.NewId())

        # The menu.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[0], text="Delete spin", icon=paths.icon_16x16.remove))

        # The menu actions.
        self.Bind(wx.EVT_MENU, self.spin_delete, id=ids[0])

        # Show the menu.
        self.PopupMenu(menu)
        menu.Destroy()


    def molecule_delete(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Call the dialog.
        self.gui.user_functions.molecule.delete(event, mol_name=self.info[1])


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
            if info[2] not in mol_ids:
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
            if info[4] not in res_ids:
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
            if info[6] not in spin_ids:
                self.tree.Delete(key)
                self.tree_ids[mol_branch_id][res_branch_id].pop(key)


    def residue_create(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Call the dialog.
        self.gui.user_functions.residue.create(event, mol_name=self.info[1])


    def residue_delete(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Call the dialog.
        self.gui.user_functions.residue.delete(event, mol_name=self.info[1], res_num=self.info[2], res_name=self.info[3])


    def spin_create(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Call the dialog.
        self.gui.user_functions.spin.create(event, mol_name=self.info[1], res_num=self.info[2], res_name=self.info[3])


    def spin_delete(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Call the dialog.
        self.gui.user_functions.spin.delete(event, mol_name=self.info[1], res_num=self.info[2], res_name=self.info[3], spin_num=self.info[4], spin_name=self.info[5])


    def update(self, pipe_name=None):
        """Update the tree view using the given data pipe."""

        # The data pipe.
        if not pipe_name:
            pipe = cdp
        else:
            pipe = get_pipe(pipe_name)

        # No data pipe, so do nothing.
        if not pipe:
            return

        # Update the molecules.
        for mol, mol_id in molecule_loop(return_id=True):
            self.update_mol(mol, mol_id)

        # Remove any deleted molecules.
        self.prune_mol()


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
            info = self.tree.GetItemPyData(key)

            # Check the mol_id for a match and, if so, terminate to speed things up.
            if mol_id == info[2]:
                new_mol = False
                mol_branch_id = key
                break

        # A new molecule.
        if new_mol:
            # Append a molecule with name to the tree.
            mol_branch_id = self.tree.AppendItem(self.root, "Molecule: %s" % mol.name)
            self.tree.SetPyData(mol_branch_id, ['mol', mol.name, mol_id])

            # Add the id to the tracking structure.
            self.tree_ids[mol_branch_id] = {}

            # Set the bitmap.
            self.tree.SetItemImage(mol_branch_id, self.icon_mol_index, wx.TreeItemIcon_Normal)
            self.tree.SetItemImage(mol_branch_id, self.icon_mol_unfold_index, wx.TreeItemIcon_Expanded)

        # Update the residues of this molecule.
        for res, res_id in residue_loop(mol_id, return_id=True):
            self.update_res(mol_branch_id, mol, res, res_id)

        # Start new molecules expanded.
        if new_mol:
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
            info = self.tree.GetItemPyData(key)

            # Check the res_id for a match and, if so, terminate to speed things up.
            if res_id == info[4]:
                new_res = False
                res_branch_id = key
                break

        # A new residue.
        if new_res:
            # Append a residue with name and number to the tree.
            res_branch_id = self.tree.AppendItem(mol_branch_id, "Residue: %s %s" % (res.num, res.name))
            self.tree.SetPyData(res_branch_id, ['res', mol.name, res.num, res.name, res_id])

            # Add the id to the tracking structure.
            self.tree_ids[mol_branch_id][res_branch_id] = {}

            # Set the bitmap.
            self.tree.SetItemImage(res_branch_id, self.icon_res_index, wx.TreeItemIcon_Normal & wx.TreeItemIcon_Expanded)

        # Update the spins of this residue.
        for spin, spin_id in spin_loop(res_id, return_id=True):
            self.update_spin(mol_branch_id, res_branch_id, mol, res, spin, spin_id)

        # Start new residues expanded.
        if new_res:
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
            info = self.tree.GetItemPyData(key)

            # Check the spin_id for a match and, if so, terminate to speed things up.
            if spin_id == info[6]:
                new_spin = False
                spin_branch_id = key
                break

        # A new spin.
        if new_spin:
            # Append a spin with name and number to the tree.
            spin_branch_id = self.tree.AppendItem(res_branch_id, "Spin: %s %s" % (spin.num, spin.name))
            self.tree.SetPyData(spin_branch_id, ['spin', mol.name, res.num, res.name, spin.num, spin.name, spin_id])

            # Add the id to the tracking structure.
            self.tree_ids[mol_branch_id][res_branch_id][spin_branch_id] = True

            # Set the bitmap.
            self.tree.SetItemImage(spin_branch_id, self.icon_spin_index, wx.TreeItemIcon_Normal & wx.TreeItemIcon_Expanded)

        # Start new spins expanded.
        if new_spin:
            self.tree.Expand(spin_branch_id)



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

        # The structure menu entry.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&delete", icon=paths.icon_16x16.remove, fn=self.gui.user_functions.structure.delete))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&load_spins", icon=paths.icon_16x16.spin, fn=self.gui.user_functions.structure.load_spins))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&read_pdb", icon=paths.icon_16x16.open, fn=self.gui.user_functions.structure.read_pdb))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&write_pdb", icon=paths.icon_16x16.save, fn=self.gui.user_functions.structure.write_pdb))
        self.menubar.Append(menu, "&structure")

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
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, id=1, text="&copy", icon=paths.icon_16x16.copy, fn=self.gui.user_functions.spin.copy))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="crea&te", icon=paths.icon_16x16.add, fn=self.gui.user_functions.spin.create))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, parent=self, text="&delete", icon=paths.icon_16x16.remove, fn=self.gui.user_functions.spin.delete))
        self.menubar.Append(menu, "&spin")


    def Show(self, show=True):
        """Change the behaviour of showing the window to update the content.

        @keyword show:  A flag which is True shows the window.
        @type show:     bool
        """

        # Add the refresh function to the user function subject object.
        self.gui.user_functions.register_observer('spin_view_refresh', self.refresh)

        # First update.
        self.refresh()

        # Then show the window using the baseclass method.
        wx.Frame.Show(self, show)


    def refresh(self, event=None):
        """Event handler for the refresh action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Update the data pipe selector.
        self.update_pipes()

        # Update the tree.
        self.tree_panel.update()


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Remove the refresh function from the user function subject object.
        self.gui.user_functions.unregister_observer('spin_view_refresh')

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

        # Init.
        pipe_switch = False

        # The selected pipe.
        if event:
            # The name of the selected pipe.
            pipe = str(event.GetString())

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
            self.gui.user_functions.interpreter.pipe.switch(pipe)

            # Update the tree view.
            self.tree_panel.update()

        # Set the pipe name to the cdp.
        self.pipe_name.SetValue(pipe)



class Tree_splitter(wx.SplitterWindow):
    """This splits the view of the tree view and spin container."""

    def __init__(self, gui, parent, id):
        """Initialise the tree splitter window.

        @param gui:     The gui object.
        @type gui:      wx object
        @param parent:  The parent wx object.
        @type parent:   wx object
        @param id:      The ID number.
        @type id:       int
        """

        # Execute the base class __init__() method.
        wx.SplitterWindow.__init__(self, parent, id, style=wx.SP_LIVE_UPDATE)

        # Add the tree view panel.
        parent.tree_panel = Mol_res_spin_tree(gui, parent=self, id=-1)

        # The container window.
        parent.container = Container(gui, parent=self, id=-1)

        # Make sure the panes cannot be hidden.
        self.SetMinimumPaneSize(100)

        # Split.
        self.SplitVertically(parent.tree_panel, parent.container, 400)
