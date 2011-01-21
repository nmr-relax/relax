###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
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
"""Module containing classes derived from those of wx."""

# Python module imports.
from os import getcwd
import wx

# relax GUI module imports.
from filedialog import openfile



class StructureTextCtrl(wx.TextCtrl):
    """Class for structural file selection."""

    def open_file(self, event):
        """Open the structural file.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the original file name in case of failure.
        backup = self.GetValue()

        # Open the file dialog.
        file_name = openfile(msg='Select PDB File', filetype='*.*', default='PDB files (*.pdb)|*.pdb|all files (*.*)|*.*')

        # Restore the original file name.
        if file_name == None:
            file_name = backup

        # Set the value.
        self.SetValue(file_name)

        # Skip the event.
        event.Skip()
