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
"""The molecule, residue, and spin containers for the spin viewer."""


# Python module imports.
from re import search
from string import replace, split
import wx

# relax module imports.
from generic_fns.mol_res_spin import generate_spin_id, return_spin

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


    def container_molecule(self, mol_name=None):
        """Build and display the molecule container

        @keyword mol_name:  The name of the molecule.
        @type mol_name:     str
        """

        # Store the args.
        self.mol_name = mol_name

        # The molecule ID.
        self.mol_id = generate_spin_id(mol_name=mol_name)

        # Create the header.
        sizer = self.header_molecule()

        # Add to the sizer.
        self.main_sizer.Add(sizer, 0, wx.ALL|wx.EXPAND, border=self.border)

        # A divider.
        line = wx.StaticLine(self, -1, (25, 50))
        self.main_sizer.Add(line, 0, wx.EXPAND|wx.ALL, border=self.border)


    def container_residue(self, mol_name=None, res_num=None, res_name=None):
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
        sizer = self.header_residue()

        # Add to the main sizer.
        self.main_sizer.Add(sizer, 0, wx.ALL|wx.EXPAND, border=self.border)

        # A divider.
        line = wx.StaticLine(self, -1, (25, 50))
        self.main_sizer.Add(line, 0, wx.EXPAND|wx.ALL, border=self.border)


    def container_spin(self, mol_name=None, res_num=None, res_name=None, spin_num=None, spin_name=None):
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
        sizer = self.header_spin()

        # Add to the main sizer.
        self.main_sizer.Add(sizer, 0, wx.ALL|wx.EXPAND, border=self.border)

        # A divider.
        line = wx.StaticLine(self, -1, (25, 50))
        self.main_sizer.Add(line, 0, wx.EXPAND|wx.ALL, border=self.border)

        # The spin container variables.
        sizer2 = self.spin_vars()
        self.main_sizer.Add(sizer2, 1, wx.ALL|wx.EXPAND, border=self.border)


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
        elif info['type'] == 'mol':
            self.container_molecule(mol_name=info['mol_name'])

        # The residue container display.
        elif info['type'] == 'res':
            self.container_residue(mol_name=info['mol_name'], res_num=info['res_num'], res_name=info['res_name'])

        # The spin container display.
        elif info['type'] == 'spin':
            self.container_spin(mol_name=info['mol_name'], res_num=info['res_num'], res_name=info['res_name'], spin_num=info['spin_num'], spin_name=info['spin_name'])

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


    def header_molecule(self):
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
        if self.select:
            path = paths.WIZARD_IMAGE_PATH + 'molecule.png'
        else:
            path = paths.WIZARD_IMAGE_PATH + 'molecule_grey.png'
        image = wx.StaticBitmap(self, -1, wx.Bitmap(path, wx.BITMAP_TYPE_ANY))
        sizer.Add(image, 0, wx.RIGHT, 0)

        # Return the sizer.
        return sizer


    def header_residue(self):
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
        if self.select:
            path = paths.WIZARD_IMAGE_PATH + 'residue.png'
        else:
            path = paths.WIZARD_IMAGE_PATH + 'residue_grey.png'
        image = wx.StaticBitmap(self, -1, wx.Bitmap(path, wx.BITMAP_TYPE_ANY))
        sizer.Add(image, 0, wx.RIGHT, 0)

        # Return the sizer.
        return sizer


    def header_spin(self):
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
        if self.select:
            path = paths.WIZARD_IMAGE_PATH + 'spin.png'
        else:
            path = paths.WIZARD_IMAGE_PATH + 'spin_grey.png'
        image = wx.StaticBitmap(self, -1, wx.Bitmap(path, wx.BITMAP_TYPE_ANY))
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
