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
import wx


class StructureTextCtrl(wx.TextCtrl):
    """Class for structural file selection."""

    def structure_pdb(self, event): # structure file
        backup = self.structure_noe1.GetValue()
        structure_file_pdb = openfile('Select PDB File', self.res_noe1.GetValue() + sep, '*.*', 'PDB files (*.pdb)|*.pdb|all files (*.*)|*.*')
        if structure_file_pdb == None:
            structure_file_pdb = backup
        self.structure_noe1.SetValue(structure_file_pdb)
        self.structure_r11.SetValue(structure_file_pdb)
        self.structure_r21.SetValue(structure_file_pdb)
        self.structure_noe1_copy.SetValue(structure_file_pdb)
        self.structure_r11_copy.SetValue(structure_file_pdb)
        self.structure_r21_copy.SetValue(structure_file_pdb)
        self.structure_noe1_copy_1.SetValue(structure_file_pdb)
        self.structure_r11_copy_1.SetValue(structure_file_pdb)
        self.structure_r21_copy_1.SetValue(structure_file_pdb)
        self.structure_r21_copy_1_copy.SetValue(structure_file_pdb)
        event.Skip()
