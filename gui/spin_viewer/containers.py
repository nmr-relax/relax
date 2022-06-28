###############################################################################
#                                                                             #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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
"""The molecule, residue, and spin containers for the spin viewer."""


# Python module imports.
from re import search
import wx

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from gui.misc import bitmap_setup
from gui.string_conv import str_to_gui
from lib.compat import unicode
from pipe_control.mol_res_spin import return_spin



class Container(wx.Window):
    """The molecule, residue, and spin container window."""

    def __init__(self, gui, parent=None, id=None):
        """Set up the container GUI element.

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
        wx.Window.__init__(self, parent, id, style=wx.BORDER_SUNKEN)

        # Set a minimum size for the window.
        self.SetMinSize((500, 500))

        # Add a sizer.
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        # Display the root panel.
        self.container = Root(self.main_sizer, self)

        # Resizing.
        self.Bind(wx.EVT_SIZE, self._resize)
        self.Bind(wx.EVT_PAINT, self._resize)


    def _resize(self, event):
        """Resize the tree element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Re-perform the window layout.
        self.Layout()
        self.Refresh()


    def display(self, info):
        """Display the info for the selected container.

        @param info:    The information list consisting of the container type ('root', 'mol', 'res', or 'spin'), the molecule name, the residue number, the residue name, the spin number, and the spin name.  The name and number information is dropped when not needed.
        @type info:     list of str and int
        """

        # Destroy all the original contents.
        self.main_sizer.Clear(True)

        # The root window display.
        if info == 'root' or info == None:
            self.container = Root(self.main_sizer, self)

        # The molecule container display.
        elif info['type'] == 'mol':
            self.container = Molecule(self.main_sizer, self, mol_name=info['mol_name'], mol_id=info['id'], select=info['select'])

        # The residue container display.
        elif info['type'] == 'res':
            self.container = Residue(self.main_sizer, self, mol_name=info['mol_name'], res_num=info['res_num'], res_name=info['res_name'], res_id=info['id'], select=info['select'])

        # The spin container display.
        elif info['type'] == 'spin':
            self.container = Spin(self.main_sizer, self, mol_name=info['mol_name'], res_num=info['res_num'], res_name=info['res_name'], spin_num=info['spin_num'], spin_name=info['spin_name'], spin_id=info['id'], select=info['select'])

        # Re-perform the window layout.
        self.Layout()
        self.Refresh()



class Container_base:
    """The base class for the molecule, residue, and spin containers."""

    # Some class variables.
    border = 10

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
        text = text.replace('&', '&&')

        # The object.
        obj = wx.StaticText(self.parent, -1, text)

        # Formatting.
        obj.SetFont(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.ITALIC, wx.NORMAL, False, 'Times'))

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
        text = text.replace('&', '&&')

        # The object.
        obj = wx.StaticText(self.parent, -1, text)

        # Formatting.
        obj.SetFont(wx.Font(16, wx.FONTFAMILY_ROMAN, wx.ITALIC, wx.NORMAL, False, 'Times'))

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
        title = wx.StaticText(self.parent, -1, text)

        # Formatting.
        title.SetFont(wx.Font(32, wx.FONTFAMILY_ROMAN, wx.ITALIC, wx.NORMAL, False, 'Times'))

        # Return the object.
        return title



class Molecule(Container_base):
    """The molecule container."""

    def __init__(self, box, parent, mol_name=None, mol_id=None, select=True):
        """Set up the molecule container.

        @param box:         The box sizer element to pack the contents into.
        @type box:          wx object
        @param parent:      The parent GUI element.
        @type parent:       wx object
        @keyword mol_name:  The name of the molecule.
        @type mol_name:     str
        @keyword mol_id:    The molecule ID string.
        @type mol_id:       str
        @keyword select:    The selection state.
        @type select:       bool
        """

        # Store the args.
        self.parent = parent
        self.mol_name = mol_name
        self.mol_id = mol_id
        self.select = select

        # Create the header.
        sizer = self.header_molecule()

        # Add to the sizer.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, border=self.border)

        # A divider.
        line = wx.StaticLine(self.parent, -1, (25, 50))
        box.Add(line, 0, wx.EXPAND|wx.ALL, border=self.border)


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
        grid_sizer = wx.FlexGridSizer(2, 2, 5, 50)
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
            path = WIZARD_IMAGE_PATH + 'molecule.png'
        else:
            path = WIZARD_IMAGE_PATH + 'molecule_grey.png'
        image = wx.StaticBitmap(self.parent, -1, bitmap_setup(path))
        sizer.Add(image, 0, wx.RIGHT, 0)

        # Return the sizer.
        return sizer



class Residue(Container_base):
    """The residue container."""

    def __init__(self, box, parent, mol_name=None, res_num=None, res_name=None, res_id=None, select=True):
        """Set up the residue container.

        @param box:         The box sizer element to pack the contents into.
        @type box:          wx object
        @param parent:      The parent GUI element.
        @type parent:       wx object
        @keyword mol_name:  The molecule name.
        @type mol_name:     str
        @keyword res_num:   The residue number.
        @type res_num:      str
        @keyword res_name:  The residue name.
        @type res_name:     str
        @keyword res_id:    The residue ID string.
        @type res_id:       str
        @keyword select:    The selection state.
        @type select:       bool
        """

        # Store the args.
        self.parent = parent
        self.mol_name = mol_name
        self.res_num = res_num
        self.res_name = res_name
        self.res_id = res_id
        self.select = select

        # Create the header.
        sizer = self.header_residue()

        # Add to the main sizer.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, border=self.border)

        # A divider.
        line = wx.StaticLine(self.parent, -1, (25, 50))
        box.Add(line, 0, wx.EXPAND|wx.ALL, border=self.border)


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
            path = WIZARD_IMAGE_PATH + 'residue.png'
        else:
            path = WIZARD_IMAGE_PATH + 'residue_grey.png'
        image = wx.StaticBitmap(self.parent, -1, bitmap_setup(path))
        sizer.Add(image, 0, wx.RIGHT, 0)

        # Return the sizer.
        return sizer



class Spin(Container_base):
    """The spin container."""

    def __init__(self, box, parent, mol_name=None, res_num=None, res_name=None, spin_num=None, spin_name=None, spin_id=None, select=True):
        """Set up the spin container.

        @param box:         The box sizer element to pack the contents into.
        @type box:          wx object
        @param parent:      The parent GUI element.
        @type parent:       wx object
        @keyword mol_name:  The molecule name.
        @type mol_name:     str
        @keyword res_num:   The residue number.
        @type res_num:      str
        @keyword res_name:  The residue name.
        @type res_name:     str
        @keyword spin_num:  The spin number.
        @type spin_num:     str
        @keyword spin_name: The spin name.
        @type spin_name:    str
        @keyword spin_id:   The spin ID string.
        @type spin_id:      str
        @keyword select:    The selection state.
        @type select:       bool
        """

        # Store the args.
        self.parent = parent
        self.mol_name = mol_name
        self.res_num = res_num
        self.res_name = res_name
        self.spin_num = spin_num
        self.spin_name = spin_name
        self.spin_id = spin_id
        self.select = select

        # Create the header.
        sizer = self.header_spin()

        # Add to the main sizer.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, border=self.border)

        # A divider.
        line = wx.StaticLine(self.parent, -1, (25, 50))
        box.Add(line, 0, wx.EXPAND|wx.ALL, border=self.border)

        # The spin container variables.
        sizer2 = self.spin_vars()
        box.Add(sizer2, 1, wx.ALL|wx.EXPAND, border=self.border)


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
            path = WIZARD_IMAGE_PATH + 'spin.png'
        else:
            path = WIZARD_IMAGE_PATH + 'spin_grey.png'
        image = wx.StaticBitmap(self.parent, -1, bitmap_setup(path))
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
        table = wx.ListCtrl(self.parent, -1, style=wx.BORDER_SUNKEN|wx.LC_REPORT)

        # The headers.
        table.InsertColumn(0, "Variable")
        table.InsertColumn(1, "Value")
        table.InsertColumn(2, "Type")

        # The widths.
        table.SetColumnWidth(0, 300)
        table.SetColumnWidth(1, 200)
        table.SetColumnWidth(2, 200)

        # The spin container.
        spin = return_spin(spin_id=self.spin_id)

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
            obj_type = str(type(obj)).split("'")[1]

            # List types.
            if obj_type in ['list', 'numpy.ndarray'] and len(obj) > 1:
                # The first row.
                table.Append((str_to_gui(name), str_to_gui("[%s," % obj[0]), str_to_gui(obj_type)))

                # The rest of the rows.
                for i in range(1, len(obj)-1):
                    table.Append((str_to_gui(''), str_to_gui(" %s," % obj[i]), str_to_gui('')))

                # The last row.
                table.Append((str_to_gui(''), str_to_gui(" %s]" % obj[-1]), str_to_gui('')))

            # Dictionary types.
            elif obj_type == 'dict':
                # The keys.
                keys = sorted(obj.keys())

                # Single entry (or None).
                if len(keys) < 2:
                    table.Append((str_to_gui(name), str_to_gui(obj), str_to_gui(obj_type)))
                    continue

                # The first row.
                table.Append((str_to_gui(name), str_to_gui("{'%s': %s," % (keys[0], obj[keys[0]])), str_to_gui(obj_type)))

                # The rest of the rows.
                for i in range(1, len(keys)-1):
                    table.Append((str_to_gui(''), str_to_gui(" '%s': %s," % (keys[i], obj[keys[i]])), str_to_gui('')))

                # The last row.
                table.Append((str_to_gui(''), str_to_gui(" '%s': %s}" % (keys[-1], obj[keys[-1]])), str_to_gui('')))

            # All other data types.
            else:
                table.Append((str_to_gui(name), str_to_gui(obj), str_to_gui(obj_type)))

        # Add the table to the sizer.
        sizer.Add(table, 1, wx.ALL|wx.EXPAND, 0)

        # Return the sizer.
        return sizer



class Root(Container_base):
    """The root container."""

    def __init__(self, box, parent):
        """Set up the root container.

        @param box:         The box sizer element to pack the contents into.
        @type box:          wx object
        @param parent:      The parent GUI element.
        @type parent:       wx object
        """

        # Store the arg.
        self.parent = parent

        # A sizer for the header.
        sizer = wx.BoxSizer(wx.VERTICAL)

        # The title
        title = self.create_title("The spin view window")
        sizer.Add(title, 0, wx.LEFT, 0)

        # Add to the sizer.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, border=self.border)
