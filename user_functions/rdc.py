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
"""The rdc user function definitions."""

# Python module imports.
import wx

# relax module imports.
from generic_fns import align_tensor, pipes, rdc
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('rdc')
uf_class.title = "Class for handling residual dipolar couplings."
uf_class.menu_text = "&rdc"
uf_class.gui_icon = "relax.align_tensor"


# The rdc.back_calc user function.
uf = uf_info.add_uf('rdc.back_calc')
uf.title = "Back calculate the residual dipolar couplings."
uf.title_short = "RDC back calculation."
uf.display = True
uf.add_keyarg(
    name = "align_id",
    py_type = "str",
    desc_short = "alignment ID string",
    desc = "The alignment ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = align_tensor.get_ids,
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will back calculate the residual dipolar couplings (RDCs) if an alignment tensor is present and inter-dipole vectors have been loaded into the relax data store.")
uf.backend = rdc.back_calc
uf.menu_text = "&back_calc"
uf.gui_icon = "oxygen.categories.applications-education"
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'
uf.wizard_apply_button = False


# The rdc.calc_q_factors user function.
uf = uf_info.add_uf('rdc.calc_q_factors')
uf.title = "Calculate the RDC Q factor for the selected spins."
uf.title_short = "RDC Q factor calculation."
uf.display = True
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin ID string for restricting to subset of all selected spins.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("For this to work, the back-calculated RDC data must first be generated by the analysis specific code.  Otherwise a warning will be given.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To calculate the RDC Q factor for only the spins '@H26', '@H27', and '@H28', type one of:")
uf.desc[-1].add_prompt("relax> rdc.calc_q_factors('@H26 & @H27 & @H28')")
uf.desc[-1].add_prompt("relax> rdc.calc_q_factors(spin_id='@H26 & @H27 & @H28')")
uf.backend = rdc.q_factors
uf.menu_text = "&calc_q_factors"
uf.gui_icon = "oxygen.categories.applications-education"
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'
uf.wizard_apply_button = False


# No backend!
## The rdc.copy user function.
#uf = uf_info.add_uf('rdc.copy')
#uf.title = "Copy RDC data from one data pipe to another."
#uf.title_short = "RDC copying."
#uf.add_keyarg(
#    name = "pipe_from",
#    py_type = "str",
#    desc_short = "source pipe",
#    desc = "The name of the pipe to copy the RDC data from.",
#    wiz_element_type = 'combo',
#    wiz_combo_iter = pipes.pipe_names,
#    can_be_none = True
#)
#uf.add_keyarg(
#    name = "pipe_to",
#    py_type = "str",
#    desc_short = "destination pipe",
#    desc = "The name of the pipe to copy the RDC data to.",
#    wiz_element_type = 'combo',
#    wiz_combo_iter = pipes.pipe_names,
#    can_be_none = True
#)
#uf.add_keyarg(
#    name = "align_id",
#    py_type = "str",
#    desc_short = "alignment ID string",
#    desc = "The alignment ID string.",
#    wiz_element_type = 'combo',
#    wiz_combo_iter = align_tensor.get_ids,
#    wiz_read_only = True,
#    can_be_none = True
#)
## Description.
#uf.desc.append(Desc_container())
#uf.desc[-1].add_paragraph("This function will copy RDC data from 'pipe_from' to 'pipe_to'.  If align_id is not given then all RDC data will be copied, otherwise only a specific data set will be.")
## Prompt examples.
#uf.desc.append(Desc_container("Prompt examples"))
#uf.desc[-1].add_paragraph("To copy all RDC data from pipe 'm1' to pipe 'm9', type one of:")
#uf.desc[-1].add_prompt("relax> rdc.copy('m1', 'm9')")
#uf.desc[-1].add_prompt("relax> rdc.copy(pipe_from='m1', pipe_to='m9')")
#uf.desc[-1].add_prompt("relax> rdc.copy('m1', 'm9', None)")
#uf.desc[-1].add_prompt("relax> rdc.copy(pipe_from='m1', pipe_to='m9', align_id=None)")
#uf.desc[-1].add_paragraph("To copy only the 'Th' RDC data from 'm3' to 'm6', type one of:")
#uf.desc[-1].add_prompt("relax> rdc.copy('m3', 'm6', 'Th')")
#uf.desc[-1].add_prompt("relax> rdc.copy(pipe_from='m3', pipe_to='m6', align_id='Th')")
#uf.backend = rdc.copy
#uf.menu_text = "cop&y"
#uf.gui_icon = "oxygen.actions.list-add"
#uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'


# The rdc.corr_plot user function.
uf = uf_info.add_uf('rdc.corr_plot')
uf.title = "Generate a correlation plot of the measured vs. the back-calculated RDCs."
uf.title_short = "Correlation plot generation."
uf.add_keyarg(
    name = "format",
    default = "grace",
    py_type = "str",
    desc_short = "format",
    desc = "The format of the plot data.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["grace"],
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "file",
    default = "rdc_corr_plot.agr",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "Grace file name",
    desc = "The name of the Grace file to create.",
    wiz_filesel_wildcard = "Grace files (*.agr)|*.agr;*.AGR",
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
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if True will cause the file to be overwritten."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Two formats are currently supported.  If format is set to 'grace', then a Grace plot file will be created.  If the format is not set then a plain text list of the measured and back-calculated data will be created.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To create a Grace plot of the data, type:")
uf.desc[-1].add_prompt("relax> rdc.corr_plot()")
uf.desc[-1].add_paragraph("To create a plain text list of the measured and back-calculated data, type one of:")
uf.desc[-1].add_prompt("relax> rdc.corr_plot(None)")
uf.desc[-1].add_prompt("relax> rdc.corr_plot(format=None)")
uf.backend = rdc.corr_plot
uf.menu_text = "corr_&plot"
uf.wizard_size = (800, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'
uf.wizard_apply_button = False


# The rdc.delete user function.
uf = uf_info.add_uf('rdc.delete')
uf.title = "Delete the RDC data corresponding to the alignment ID."
uf.title_short = "RDC deletion."
uf.add_keyarg(
    name = "align_id",
    py_type = "str",
    desc_short = "alignment ID string",
    desc = "The alignment ID string of the data to delete.",
    wiz_element_type = 'combo',
    wiz_combo_iter = align_tensor.get_ids,
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will delete all RDC data associated with the alignment ID in the current data pipe.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To delete the RDC data corresponding to align_id='PH_gel', type:")
uf.desc[-1].add_prompt("relax> rdc.delete('PH_gel')")
uf.backend = rdc.delete
uf.menu_text = "&delete"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'


# The rdc.display user function.
uf = uf_info.add_uf('rdc.display')
uf.title = "Display the RDC data corresponding to the alignment ID."
uf.title_short = "RDC data display."
uf.display = True
uf.add_keyarg(
    name = "align_id",
    py_type = "str",
    desc_short = "alignment ID string",
    desc = "The alignment ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = align_tensor.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "bc",
    default = False,
    py_type = "bool",
    desc_short = "back-calculation flag",
    desc = "A flag which if set will display the back-calculated rather than measured RDCs."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will display all of the RDC data associated with the alignment ID in the current data pipe.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To display the 'phage' RDC data, type:")
uf.desc[-1].add_prompt("relax> rdc.display('phage')")
uf.backend = rdc.display
uf.menu_text = "di&splay"
uf.gui_icon = "oxygen.actions.document-preview"
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'


# The rdc.read user function.
uf = uf_info.add_uf('rdc.read')
uf.title = "Read the RDC data from file."
uf.title_short = "RDC data reading."
uf.add_keyarg(
    name = "align_id",
    py_type = "str",
    desc_short = "alignment ID string",
    desc = "The alignment ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = align_tensor.get_ids
)
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file containing the RDC data.",
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
    name = "data_type",
    default = "D",
    py_type = "str",
    desc_short = "data type",
    desc = "Specify if the RDC data is in the D or 2D format.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["D", "2D"],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "spin_id1_col",
    default = 1,
    py_type = "int",
    min = 1,
    desc_short = "first spin ID column",
    desc = "The spin ID string column for the first spin."
)
uf.add_keyarg(
    name = "spin_id2_col",
    default = 2,
    py_type = "int",
    min = 1,
    desc_short = "second spin ID column",
    desc = "The spin ID string column for the second spin."
)
uf.add_keyarg(
    name = "data_col",
    py_type = "int",
    desc_short = "data column",
    desc = "The RDC data column.",
    can_be_none = True
)
uf.add_keyarg(
    name = "error_col",
    py_type = "int",
    desc_short = "error column",
    desc = "The experimental error column.",
    can_be_none = True
)
uf.add_keyarg(
    name = "sep",
    py_type = "str",
    desc_short = "column separator",
    desc = "The column separator (the default is white space).",
    wiz_element_type = "combo",
    wiz_combo_choices = ["white space", ",", ";", ":"],
    wiz_combo_data = [None, ",", ";", ":"],
    wiz_read_only = False,
    can_be_none = True
)
uf.add_keyarg(
    name = "neg_g_corr",
    default = False,
    py_type = "bool",
    desc_short = "negative gyromagnetic ratio correction",
    desc = "A flag which is used to correct for the negative gyromagnetic ratio of 15N.  If set to True, all RDC values will be inverted prior to being stored in the relax data store."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will read RDC data from a file and associate it with an alignment ID, either a new ID or a preexisting one with no RDC data.")
uf.desc[-1].add_paragraph("The data type is used to specify how the RDC is defined.  It can be set to two values:")
uf.desc[-1].add_list_element("'D' means that the splitting in the aligned sample was taken as J + D.")
uf.desc[-1].add_list_element("'2D' means that the splitting in the aligned sample was assumed to be J + 2D.")
uf.desc[-1].add_paragraph("Internally, relax uses the D notation.  Therefore if set to '2D', the values will be doubled when read in.")
uf.desc[-1].add_paragraph("If the negative gyromagnetic ratio correction flag is set, a sign inversion will be applied to all RDC values to be loaded.  This is sometimes needed for 15N if the data is not compensated for the negative gyromagnetic ratio.")
uf.desc[-1].add_paragraph("The spin system can be identified in the file using two different formats.  The first is the spin ID string column which can include the molecule name, the residue name and number, and the spin name and number.  Alternatively the molecule name, residue number and name, and spin number and name columns can be supplied allowing this information to be in separate columns.  Note that the numbering of columns starts at one.  The spin ID can be used to restrict the reading to certain spin types, for example only 15N spins when only residue information is in the file.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following commands will read the RDC data out of the file 'Tb.txt' where the columns are separated by the symbol ',', and store the RDCs under the ID 'Tb':")
uf.desc[-1].add_prompt("relax> rdc.read('Tb', 'Tb.txt', sep=',')")
uf.desc[-1].add_paragraph("If the individual spin RDC errors are located in the file 'rdc_err.txt' in column number 5, then to read these values into relax, assuming J + D was measured, type one of:")
uf.desc[-1].add_prompt("relax> rdc.read('phage', 'rdc_err.txt', data_type='D', error_col=5)")
uf.desc[-1].add_prompt("relax> rdc.read(align_id='phage', file='rdc_err.txt', data_type='D', error_col=5)")
uf.desc[-1].add_paragraph("If the RDCs correspond to the 'N' spin and other spin types such as 1H, 13C, etc. are loaded into relax, then type:")
uf.desc[-1].add_prompt("relax> rdc.read('Tb', 'Tb.txt', spin_id='@N')")
uf.backend = rdc.read
uf.menu_text = "&read"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_height_desc = 300
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'


# The rdc.weight user function.
uf = uf_info.add_uf('rdc.weight')
uf.title = "Set optimisation weights on the RDC data."
uf.title_short = "RDC weighting."
uf.add_keyarg(
    name = "align_id",
    py_type = "str",
    desc_short = "alignment ID string",
    desc = "The alignment ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = align_tensor.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin ID string."
)
uf.add_keyarg(
    name = "weight",
    default = 1.0,
    py_type = "num",
    desc_short = "weight",
    desc = "The weighting value."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This can be used to force the RDC to contribute more or less to the chi-squared optimisation statistic.  The higher the value, the more importance the RDC will have.")
uf.backend = rdc.weight
uf.menu_text = "wei&ght"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'


# The rdc.write user function.
uf = uf_info.add_uf('rdc.write')
uf.title = "Write the RDC data to file."
uf.title_short = "RDC data writing."
uf.add_keyarg(
    name = "align_id",
    py_type = "str",
    desc_short = "alignment ID string",
    desc = "The alignment ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = align_tensor.get_ids,
    wiz_read_only = True
)
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
    name = "bc",
    default = False,
    py_type = "bool",
    desc_short = "back-calculation flag",
    desc = "A flag which if set will write out the back-calculated rather than measured RDCs."
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
uf.desc[-1].add_paragraph("If no directory name is given, the file will be placed in the current working directory.  The alignment ID is required for selecting which RDC data set will be written to file.")
uf.backend = rdc.write
uf.menu_text = "&write"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'
