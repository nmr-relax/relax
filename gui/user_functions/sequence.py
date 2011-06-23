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
"""The sequence user function GUI elements."""

# Python module imports.
from string import split

# relax module imports.
from generic_fns import pipes

# GUI module imports.
from base import UF_base, UF_page
from gui.paths import WIZARD_IMAGE_PATH
from gui.misc import gui_to_int, gui_to_str
from gui.wizard import Wiz_window


# The container class.
class Sequence(UF_base):
    """The container class for holding all GUI elements."""

    def read(self, event):
        """The sequence.delete user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title='Read the spin sequence from a file')
        page = Read_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)
        wizard.run()



class Read_page(UF_page):
    """The sequence.delete() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'sequence.png'
    main_text = 'This dialog allows you to read the molecule, residue, and spin information from a file.'
    title = 'Sequence reading'


    def add_contents(self, sizer):
        """Add the sequence specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The sequence file:", title="Sequence file selection")

        # The parameter file settings.
        self.free_file_format(sizer)

        # The spin ID restriction.
        self.spin_id = self.input_field(sizer, "Restrict data loading to certain spins:", tooltip="This must be a valid spin ID.  Multiple spins can be selected using ranges, the '|' operator, residue ranges, etc.")


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetValue())

        # No file.
        if not file:
            return

        # Get the column numbers.
        spin_id_col =   gui_to_int(self.spin_id_col.GetValue())
        mol_name_col =  gui_to_int(self.mol_name_col.GetValue())
        res_num_col =   gui_to_int(self.res_num_col.GetValue())
        res_name_col =  gui_to_int(self.res_name_col.GetValue())
        spin_num_col =  gui_to_int(self.spin_num_col.GetValue())
        spin_name_col = gui_to_int(self.spin_name_col.GetValue())

        # The column separator.
        sep = str(self.sep.GetValue())
        if sep == 'white space':
            sep = None

        # The spin ID.
        spin_id = gui_to_str(self.spin_id.GetValue())

        # Read the sequence.
        self.interpreter.sequence.read(file=file, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, spin_id=spin_id)
