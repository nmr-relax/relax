###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""The sequence user function definitions."""

# Python module imports.
import wx

# relax module imports.
from generic_fns import pipes, sequence
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('sequence')
uf_class.title = "Class for manipulating sequence data."
uf_class.menu_text = "&sequence"
uf_class.gui_icon = "relax.sequence"


# The sequence.copy user function.
uf = uf_info.add_uf('sequence.copy')
uf.title = "Copy the molecule, residue, and spin sequence data from one data pipe to another."
uf.title_short = "Sequence data copying."
uf.add_keyarg(
    name = "pipe_from",
    py_type = "str",
    desc_short = "source data pipe",
    desc = "The name of the data pipe to copy the sequence data from.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "pipe_to",
    py_type = "str",
    desc_short = "destination data pipe",
    desc = "The name of the data pipe to copy the sequence data to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will copy the sequence data between data pipes.  The destination data pipe must not contain any sequence data.  If the source and destination pipes are not specified, then both will default to the current data pipe (hence providing one is essential).")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To copy the sequence from the data pipe 'm1' to the current data pipe, type:")
uf.desc[-1].add_prompt("relax> sequence.copy('m1')")
uf.desc[-1].add_prompt("relax> sequence.copy(pipe_from='m1')")
uf.desc[-1].add_paragraph("To copy the sequence from the current data pipe to the data pipe 'm9', type:")
uf.desc[-1].add_prompt("relax> sequence.copy(pipe_to='m9')")
uf.desc[-1].add_paragraph("To copy the sequence from the data pipe 'm1' to 'm2', type:")
uf.desc[-1].add_prompt("relax> sequence.copy('m1', 'm2')")
uf.desc[-1].add_prompt("relax> sequence.copy(pipe_from='m1', pipe_to='m2')")
uf.backend = sequence.copy
uf.menu_text = "&copy"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'sequence.png'


# The sequence.display user function.
uf = uf_info.add_uf('sequence.display')
uf.title = "Display sequences of molecules, residues, and/or spins."
uf.title_short = "Sequence data display."
uf.display = True
uf.add_keyarg(
    name = "sep",
    py_type = "str",
    desc_short = "column separator",
    desc = "The column separator (the default of None corresponds to white space).",
    can_be_none = True
)
uf.add_keyarg(
    name = "mol_name_flag",
    default = True,
    py_type = "bool",
    desc_short = "molecule name flag",
    desc = "A flag which if True will cause the molecule name column to be shown."
)
uf.add_keyarg(
    name = "res_num_flag",
    default = True,
    py_type = "bool",
    desc_short = "residue number flag",
    desc = "A flag which if True will cause the residue number column to be shown."
)
uf.add_keyarg(
    name = "res_name_flag",
    default = True,
    py_type = "bool",
    desc_short = "residue name flag",
    desc = "A flag which if True will cause the residue name column to be shown."
)
uf.add_keyarg(
    name = "spin_num_flag",
    default = True,
    py_type = "bool",
    desc_short = "spin number flag",
    desc = "A flag which if True will cause the spin number column to be shown."
)
uf.add_keyarg(
    name = "spin_name_flag",
    default = True,
    py_type = "bool",
    desc_short = "spin name flag",
    desc = "A flag which if True will cause the spin name column to be shown."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will print out the sequence information of all loaded spins in the current data pipe.")
uf.backend = sequence.display
uf.menu_text = "&display"
uf.gui_icon = "oxygen.actions.document-preview"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'sequence.png'
uf.wizard_apply_button = False


# The sequence.read user function.
uf = uf_info.add_uf('sequence.read')
uf.title = "Read the molecule, residue, and spin sequence from a file."
uf.title_short = "Sequence data reading."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file containing the sequence data.",
    wiz_filesel_style = wx.FD_OPEN
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory where the file is located.",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin ID column",
    desc = "The spin ID string column (an alternative to the mol, res, and spin name and number columns).",
    can_be_none = True
)
uf.add_keyarg(
    name = "mol_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "molecule name column",
    desc = "The molecule name column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "res_num_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "residue number column",
    desc = "The residue number column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "res_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "residue name column",
    desc = "The residue name column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_num_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin number column",
    desc = "The spin number column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin name column",
    desc = "The spin name column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "sep",
    py_type = "str",
    arg_type = "free format",
    desc_short = "column separator",
    desc = "The column separator (the default is white space).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin ID string to restrict the loading of data to certain spin subsets.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The spin system can be identified in the file using two different formats.  The first is the spin ID string column which can include the molecule name, the residue name and number, and the spin name and number.  Alternatively the molecule name, residue number, residue name, spin number and/or spin name columns can be supplied allowing this information to be in separate columns.  Note that the numbering of columns starts at one.  The spin ID string can be used to restrict the reading to certain spin types, for example only 15N spins when only residue information is in the file.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following commands will read protein backbone 15N sequence data out of a file called 'seq' where the residue numbers and names are in the first and second columns respectively:")
uf.desc[-1].add_prompt("relax> sequence.read('seq')")
uf.desc[-1].add_prompt("relax> sequence.read('seq', res_num_col=1, res_name_col=2)")
uf.desc[-1].add_prompt("relax> sequence.read(file='seq', res_num_col=1, res_name_col=2, sep=None)")
uf.desc[-1].add_paragraph("The following commands will read the residue sequence out of the file 'noe.out' which also contains the NOE values:")
uf.desc[-1].add_prompt("relax> sequence.read('noe.out')")
uf.desc[-1].add_prompt("relax> sequence.read('noe.out', res_num_col=1, res_name_col=2)")
uf.desc[-1].add_prompt("relax> sequence.read(file='noe.out', res_num_col=1, res_name_col=2)")
uf.desc[-1].add_paragraph("The following commands will read the sequence out of the file 'noe.600.out' where the residue numbers are in the second column, the names are in the sixth column and the columns are separated by commas:")
uf.desc[-1].add_prompt("relax> sequence.read('noe.600.out', res_num_col=2, res_name_col=6, sep=',')")
uf.desc[-1].add_prompt("relax> sequence.read(file='noe.600.out', res_num_col=2, res_name_col=6, sep=',')")
uf.desc[-1].add_paragraph("The following commands will read the RNA residues and atoms (including C2, C5, C6, C8, N1, and N3) from the file '500.NOE', where the residue number, residue name, spin number, and spin name are in the first to fourth columns respectively:")
uf.desc[-1].add_prompt("relax> sequence.read('500.NOE', res_num_col=1, res_name_col=2, spin_num_col=3, spin_name_col=4)")
uf.desc[-1].add_prompt("relax> sequence.read(file='500.NOE', res_num_col=1, res_name_col=2, spin_num_col=3, spin_name_col=4)")
uf.backend = sequence.read
uf.menu_text = "&read"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'sequence.png'
uf.wizard_apply_button = False


# The sequence.write user function.
uf = uf_info.add_uf('sequence.write')
uf.title = "Write the molecule, residue, and spin sequence to a file."
uf.title_short = "Sequence data writing."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file.",
    wiz_filesel_style = wx.FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory name.",
    can_be_none = True
)
uf.add_keyarg(
    name = "sep",
    py_type = "str",
    desc_short = "column separator",
    desc = "The column separator (the default of None corresponds to white space).",
    can_be_none = True
)
uf.add_keyarg(
    name = "mol_name_flag",
    default = True,
    py_type = "bool",
    desc_short = "molecule name flag",
    desc = "A flag which if True will cause the molecule name column to be shown."
)
uf.add_keyarg(
    name = "res_num_flag",
    default = True,
    py_type = "bool",
    desc_short = "residue number flag",
    desc = "A flag which if True will cause the residue number column to be shown."
)
uf.add_keyarg(
    name = "res_name_flag",
    default = True,
    py_type = "bool",
    desc_short = "residue name flag",
    desc = "A flag which if True will cause the residue name column to be shown."
)
uf.add_keyarg(
    name = "spin_num_flag",
    default = True,
    py_type = "bool",
    desc_short = "spin number flag",
    desc = "A flag which if True will cause the spin number column to be shown."
)
uf.add_keyarg(
    name = "spin_name_flag",
    default = True,
    py_type = "bool",
    desc_short = "spin name flag",
    desc = "A flag which if True will cause the spin name column to be shown."
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if True will cause the file to be overwritten."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Write the sequence data to file.  If no directory name is given, the file will be placed in the current working directory.")
uf.backend = sequence.write
uf.menu_text = "&write"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'sequence.png'
uf.wizard_apply_button = False
