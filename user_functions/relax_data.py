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
"""Module containing the 'relax_data' user function data."""

# relax module imports.
from generic_fns import pipes, relax_data
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('relax_data')
uf_class.title = "Class for manipulating R1, R2, and NOE relaxation data."
uf_class.menu_text = "&relax_data"
uf_class.gui_icon = "relax.fid"


# The relax_data.back_calc user function.
uf = uf_info.add_uf('relax_data.back_calc')
uf.title = "Back calculate the relaxation data at the given frequency."
uf.title_short = "Relaxation data back calculation."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation ID string",
    desc = "The relaxation data ID string."
)
uf.add_keyarg(
    name = "ri_type",
    py_type = "str",
    desc_short = "relaxation type",
    desc = "The relaxation data type, ie 'R1', 'R2', or 'NOE'.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["R1", "R2", "NOE"],
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "frq",
    py_type = "num",
    desc_short = "frequency",
    desc = "The spectrometer frequency in Hz.",
    can_be_none = True
)
uf.desc = """
This allows relaxation data of the given type and frequency to be back calculated from the model parameter values.  If the relaxation data type and frequency are not given, then relaxation data matching that currently loaded in the relax data store will be back-calculated.
"""
uf.backend = relax_data.back_calc
uf.menu_text = "&back_calc"
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'


# The relax_data.copy user function.
uf = uf_info.add_uf('relax_data.copy')
uf.title = "Copy relaxation data from one pipe to another."
uf.title_short = "Relaxation data copying."
uf.add_keyarg(
    name = "pipe_from",
    py_type = "str",
    desc_short = "pipe from",
    desc = "The name of the pipe to copy the relaxation data from.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "pipe_to",
    py_type = "str",
    desc_short = "pipe to",
    desc = "The name of the pipe to copy the relaxation data to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True,
    can_be_none = True
)
uf.desc = """
This will copy relaxation data from one data pipe to another.  If the relaxation ID data string is not given then all relaxation data will be copied, otherwise only a specific data set will be copied.
"""
uf.prompt_examples = """
To copy all relaxation data from pipe 'm1' to pipe 'm9', type one of:

relax> relax_data.copy('m1', 'm9')
relax> relax_data.copy(pipe_from='m1', pipe_to='m9')
relax> relax_data.copy('m1', 'm9', None)
relax> relax_data.copy(pipe_from='m1', pipe_to='m9', ri_id=None)

To copy only the NOE relaxation data with the ID string of 'NOE_800' from 'm3' to 'm6', type
one of:

relax> relax_data.copy('m3', 'm6', 'NOE_800')
relax> relax_data.copy(pipe_from='m3', pipe_to='m6', ri_id='NOE_800')
"""
uf.backend = relax_data.copy
uf.menu_text = "&copy"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'


# The relax_data.delete user function.
uf = uf_info.add_uf('relax_data.delete')
uf.title = "Delete the data corresponding to the relaxation data ID string."
uf.title_short = "Relaxation data deletion."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True
)
uf.desc = """
The relaxation data corresponding to the given relaxation data ID string will be removed from the current data pipe.
"""
uf.prompt_examples = """
To delete the relaxation data corresponding to the ID 'NOE_600', type:

relax> relax_data.delete('NOE_600')
"""
uf.backend = relax_data.delete
uf.menu_text = "&delete"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_size = (700, 400)
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'


# The relax_data.display user function.
uf = uf_info.add_uf('relax_data.display')
uf.title = "Display the data corresponding to the relaxation data ID string."
uf.title_short = "Displaying relaxation data."
uf.display = True
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True
)
uf.desc = """
This will display the relaxation data corresponding to the given ID.
"""
uf.prompt_examples = """
To display the NOE relaxation data at 600 MHz with the ID string 'NOE_600', type:

relax> relax_data.display('NOE_600')
"""
uf.backend = relax_data.display
uf.menu_text = "dis&play"
uf.wizard_size = (700, 400)
uf.wizard_height_desc = 140
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'


# The relax_data.peak_intensity_type user function.
uf = uf_info.add_uf('relax_data.peak_intensity_type')
uf.title = "Specify the type of peak intensity measurement used - i.e. height or volume."
uf.title_short = "Setting peak intensity type."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "type",
    default = "height",
    py_type = "str",
    desc_short = "peak intensity type",
    desc = "The peak intensity type.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["height", "volume"],
    wiz_read_only = True
)
uf.desc = """
This is essential for BMRB data deposition.  It is used to specify whether peak heights or peak volumes were measured.  The two currently allowed values for the type argument are 'height' and 'volume'.
"""
uf.backend = relax_data.peak_intensity_type
uf.menu_text = "peak_&intensity_type"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'



# The relax_data.read user function.
uf = uf_info.add_uf('relax_data.read')
uf.title = "Read R1, R2, or NOE relaxation data from a file."
uf.title_short = "Reading relaxation data from file."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation ID string",
    desc = "The relaxation data ID string.  This must be a unique identifier."
)
uf.add_keyarg(
    name = "ri_type",
    py_type = "str",
    desc_short = "relaxation type",
    desc = "The relaxation data type, i.e. 'R1', 'R2', or 'NOE'.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["R1", "R2", "NOE"],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "frq",
    py_type = "num",
    desc_short = "frequency in Hz",
    desc = "The exact proton frequency of the spectrometer in Hertz.  See the 'sfrq' parameter in the Varian procpar file or the 'SFO1' parameter in the Bruker acqus file."
)
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file containing the relaxation data."
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
    desc_short = "spin ID string column",
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
    name = "data_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "data column",
    desc = "The relaxation data column."
)
uf.add_keyarg(
    name = "error_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "error column",
    desc = "The experimental error column."
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
    wiz_element_type = "combo",
    wiz_combo_choices = ["@N", "@C"],
    can_be_none = True
)
uf.desc = """
The spin system can be identified in the file using two different formats.  The first is the spin ID string column which can include the molecule name, the residue name and number, and the spin name and number.  Alternatively the molecule name, residue number, residue name, spin number and/or spin name columns can be supplied allowing this information to be in separate columns.  Note that the numbering of columns starts at one.  The spin ID string can be used to restrict the reading to certain spin types, for example only 15N spins when only residue information is in the file.
"""
uf.prompt_examples = """
The following commands will read the protein NOE relaxation data collected at 600 MHz out of
a file called 'noe.600.out' where the residue numbers, residue names, data, errors are in
the first, second, third, and forth columns respectively.

relax> relax_data.read('NOE_600', 'NOE', 599.7 * 1e6, 'noe.600.out', res_num_col=1,
                       res_name_col=2, data_col=3, error_col=4)
relax> relax_data.read(ri_id='NOE_600', ri_type='NOE', frq=600.0 * 1e6, file='noe.600.out',
                       res_num_col=1, res_name_col=2, data_col=3, error_col=4)


The following commands will read the R2 data out of the file 'r2.out' where the residue
numbers, residue names, data, errors are in the second, third, fifth, and sixth columns
respectively.  The columns are separated by commas.

relax> relax_data.read('R2_800', 'R2', 8.0 * 1e8, 'r2.out', res_num_col=2, res_name_col=3,
                       data_col=5, error_col=6, sep=',')
relax> relax_data.read(ri_id='R2_800', ri_type='R2', frq=8.0*1e8, file='r2.out',
                       res_num_col=2, res_name_col=3, data_col=5, error_col=6, sep=',')


The following commands will read the R1 data out of the file 'r1.out' where the columns are
separated by the symbol '%'

relax> relax_data.read('R1_300', 'R1', 300.1 * 1e6, 'r1.out', sep='%')
"""
uf.backend = relax_data.read
uf.menu_text = "&read"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_height_desc = 140
uf.wizard_size = (1000, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'


# The relax_data.temp_calibration user function.
uf = uf_info.add_uf('relax_data.temp_calibration')
uf.title = "Specify the temperature calibration method used."
uf.title_short = "Setting temperature calibration method."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "method",
    py_type = "str",
    desc_short = "temperature calibration method",
    desc = "The calibration method.",
    wiz_element_type = 'combo',
    wiz_combo_choices = [
        'methanol',
        'monoethylene glycol',
        'no calibration applied'
    ]
)
uf.desc = """
This is essential for BMRB data deposition.  The currently allowed methods are:

    'methanol',
    'monoethylene glycol',
    'no calibration applied'.

Other strings will be accepted if supplied.
"""
uf.backend = relax_data.temp_calibration
uf.menu_text = "&temp_calibration"
uf.wizard_size = (900, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'


# The relax_data.temp_control user function.
uf = uf_info.add_uf('relax_data.temp_control')
uf.title = "Specify the temperature control method used."
uf.title_short = "Setting temperature control method."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "method",
    py_type = "str",
    desc_short = "temperature control method",
    desc = "The control method.",
    wiz_element_type = 'combo',
    wiz_combo_choices = [
        'single scan interleaving',
        'temperature compensation block',
        'single scan interleaving and temperature compensation block',
        'single fid interleaving',
        'single experiment interleaving',
        'no temperature control applied'
    ],
    wiz_read_only = True
)
uf.desc = """
This is essential for BMRB data deposition.  The currently allowed methods are:

    'single scan interleaving',
    'temperature compensation block',
    'single scan interleaving and temperature compensation block',
    'single fid interleaving',
    'single experiment interleaving',
    'no temperature control applied'.
"""
uf.backend = relax_data.temp_control
uf.menu_text = "temp_contro&l"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'


# The relax_data.write user function.
uf = uf_info.add_uf('relax_data.write')
uf.title = "Write relaxation data to a file."
uf.title_short = "Relaxation data writing."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file."
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
    name = "bc",
    default = False,
    py_type = "bool",
    desc_short = "back calculated data flag",
    desc = "A flag which if True will cause the back-calculated data to be written to the file."
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if True will cause the file to be overwritten."
)
uf.desc = """
If no directory name is given, the file will be placed in the current working directory.  The relaxation data ID string is required for selecting which relaxation data to write to file.
"""
uf.backend = relax_data.write
uf.menu_text = "&write"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'
