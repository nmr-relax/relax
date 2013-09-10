###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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
"""The value user function definitions."""

# Python module imports.
from os import sep
import dep_check
if dep_check.wx_module:
    from wx import FD_OPEN, FD_SAVE
else:
    FD_OPEN = -1
    FD_SAVE = -1

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from pipe_control import diffusion_tensor, pipes, value
from prompt.doc_string import regexp_doc
from specific_analyses.consistency_tests import Consistency_tests
from specific_analyses.jw_mapping import Jw_mapping
from specific_analyses.model_free import Model_free
from specific_analyses.relax_fit import Relax_fit
from specific_analyses.n_state_model import N_state_model
from specific_analyses.noe import Noe
from specific_analyses.relax_disp.api import Relax_disp
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('value')
uf_class.title = "Class for setting data values."
uf_class.menu_text = "&value"
uf_class.gui_icon = "relax.value"


# The value.copy user function.
uf = uf_info.add_uf('value.copy')
uf.title = "Copy spin specific data values from one data pipe to another."
uf.title_short = "Value copying."
uf.add_keyarg(
    name = "pipe_from",
    py_type = "str",
    desc_short = "source data pipe",
    desc = "The name of the pipe to copy from.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "pipe_to",
    py_type = "str",
    desc_short = "destination data pipe",
    desc = "The name of the pipe to copy to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "param",
    py_type = "str",
    desc_short = "parameter",
    desc = "The parameter to copy.  Only one parameter may be selected.",
    wiz_element_type = 'combo',
    wiz_combo_iter = value.get_parameters,
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("If this is used to change values of previously minimised parameters, then the minimisation statistics (chi-squared value, iteration count, function count, gradient count, and Hessian count) will be reset.")
# Prompt examples.
uf.desc.append(regexp_doc)
uf.desc.append(Model_free.set_doc)
uf.desc.append(Model_free.return_data_name_doc)
uf.desc.append(Jw_mapping.set_doc)
uf.desc.append(Jw_mapping.return_data_name_doc)
uf.desc.append(Consistency_tests.set_doc)
uf.desc.append(Consistency_tests.return_data_name_doc)
uf.desc.append(Relax_fit.set_doc)
uf.desc.append(Relax_fit.return_data_name_doc)
uf.desc.append(N_state_model.set_doc)
uf.desc.append(N_state_model.return_data_name_doc)
uf.desc.append(Relax_disp.set_doc)
uf.desc.append(Relax_disp.return_data_name_doc)
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To copy the CSA values from the data pipe 'm1' to 'm2', type:")
uf.desc[-1].add_prompt("relax> value.copy('m1', 'm2', 'csa')")
uf.backend = value.copy
uf.menu_text = "&copy"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 500
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'value' + sep + 'value.png'


# The value.display user function.
uf = uf_info.add_uf('value.display')
uf.title = "Display spin specific data values."
uf.title_short = "Display values."
uf.display = True
uf.add_keyarg(
    name = "param",
    py_type = "str",
    desc_short = "parameter",
    desc = "The parameter to display.  Only one parameter may be selected.",
    wiz_element_type = 'combo',
    wiz_combo_iter = value.get_parameters,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "scaling",
    default = 1.0,
    py_type = "float",
    desc_short = "scaling",
    desc = "The factor to scale parameters by."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The values corresponding to the given parameter will be displayed.  The scaling argument can be used to scale the parameter values.  This can be useful for example in the case of the model-free Rex parameter to obtain the spectrometer dependent value from the omega_ex field strength independent internal value.  Or to scale correlation times from seconds down to nanosecond or picosecond timescales.")
uf.desc.append(regexp_doc)
uf.desc.append(Model_free.return_data_name_doc)
uf.desc.append(Model_free.write_doc)
uf.desc.append(Jw_mapping.return_data_name_doc)
uf.desc.append(Consistency_tests.return_data_name_doc)
uf.desc.append(Noe.return_data_name_doc)
uf.desc.append(Relax_fit.return_data_name_doc)
uf.desc.append(N_state_model.return_data_name_doc)
uf.desc.append(Relax_disp.return_data_name_doc)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To show all CSA values, type:")
uf.desc[-1].add_prompt("relax> value.display('csa')")
uf.desc[-1].add_paragraph("To display the model-free Rex values scaled to 600 MHz, type one of:")
uf.desc[-1].add_prompt("relax> value.display('rex', scaling=(2.0*pi*600e6)**2)")
uf.desc[-1].add_prompt("relax> value.display(param='rex', scaling=(2.0*pi*600e6)**2)")
uf.backend = value.display
uf.menu_text = "&display"
uf.gui_icon = "oxygen.actions.document-preview"
uf.wizard_height_desc = 550
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'value' + sep + 'value.png'


# The value.read user function.
uf = uf_info.add_uf('value.read')
uf.title = "Read spin specific data values from a file."
uf.title_short = "Reading values from file."
uf.add_keyarg(
    name = "param",
    py_type = "str",
    desc_short = "parameter",
    desc = "The parameter.  Only one parameter may be selected.",
    wiz_element_type = 'combo',
    wiz_combo_iter = value.get_parameters,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "scaling",
    default = 1.0,
    py_type = "float",
    desc_short = "scaling",
    desc = "The factor to scale parameters by."
)
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file containing the values.",
    wiz_filesel_style = FD_OPEN
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
    desc = "The RDC data column.",
    can_be_none = True
)
uf.add_keyarg(
    name = "error_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "error column",
    desc = "The experimental error column.",
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
    desc = "The spin ID string to restrict the loading of data to certain spin subsets."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The spin system can be identified in the file using two different formats.  The first is the spin ID string column which can include the molecule name, the residue name and number, and the spin name and number.  Alternatively the molecule name, residue number, residue name, spin number and/or spin name columns can be supplied allowing this information to be in separate columns.  Note that the numbering of columns starts at one.  The spin ID string can be used to restrict the reading to certain spin types, for example only 15N spins when only residue information is in the file.")
uf.desc[-1].add_paragraph("If this is used to change values of previously minimised parameters, then the minimisation statistics (chi-squared value, iteration count, function count, gradient count, and Hessian count) will be reset.")
uf.desc.append(regexp_doc)
uf.desc.append(Model_free.set_doc)
uf.desc.append(Model_free.return_data_name_doc)
uf.desc.append(Jw_mapping.set_doc)
uf.desc.append(Jw_mapping.return_data_name_doc)
uf.desc.append(Consistency_tests.set_doc)
uf.desc.append(Consistency_tests.return_data_name_doc)
uf.desc.append(Relax_fit.set_doc)
uf.desc.append(Relax_fit.return_data_name_doc)
uf.desc.append(N_state_model.set_doc)
uf.desc.append(N_state_model.return_data_name_doc)
uf.desc.append(Relax_disp.set_doc)
uf.desc.append(Relax_disp.return_data_name_doc)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To load 15N CSA values from the file 'csa_values' in the directory 'data', where spins are only identified by residue name and number, type one of the following:")
uf.desc[-1].add_prompt("relax> value.read('csa', 'data/csa_value', spin_id='@N')")
uf.desc[-1].add_prompt("relax> value.read('csa', 'csa_value', dir='data', spin_id='@N')")
uf.desc[-1].add_prompt("relax> value.read(param='csa', file='csa_value', dir='data', res_num_col=1, res_name_col=2, data_col=3, error_col=4, spin_id='@N')")
uf.backend = value.read
uf.menu_text = "&read"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_height_desc = 450
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'value' + sep + 'value.png'


# The value.set user function.
uf = uf_info.add_uf('value.set')
uf.title = "Set spin specific data values."
uf.title_short = "Value setting."
uf.add_keyarg(
    name = "val",
    py_type = "val_or_list",
    desc_short = "value",
    desc = "The value(s).",
    can_be_none = True
)
uf.add_keyarg(
    name = "param",
    py_type = "str_or_str_list",
    desc_short = "parameter",
    desc = "The parameter(s).",
    wiz_element_type = 'combo_list',
    wiz_combo_iter = value.get_parameters,
    wiz_read_only = False,
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "spin ID to restrict value setting to",
    desc = "The spin ID string to restrict value setting to.",
    can_be_none = True
)
uf.add_keyarg(
    name = "error",
    default = False,
    py_type = "bool",
    desc_short = "error flag",
    desc = "A flag which if True will cause the error rather than parameter to be set."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("If this function is used to change values of previously minimised results, then the minimisation statistics (chi-squared value, iteration count, function count, gradient count, and Hessian count) will be reset to None.")
uf.desc[-1].add_paragraph("The value can be None, a single value, or an array of values while the parameter can be None, a string, or array of strings.  The choice of which combination determines the behaviour of this function.  The following table describes what occurs in each instance.  In these columns, 'None' corresponds to None, '1' corresponds to either a single value or single string, and 'n' corresponds to either an array of values or an array of strings.")
table = uf_tables.add_table(label="table: value.set combinations", caption="The value and parameter combination options for the value.set user function.", caption_short="The value and parameter combinations for the value.set user function.")
table.add_headings(["Value", "Param", "Description"])
table.add_row(["None", "None", "This case is used to set the model parameters prior to minimisation or calculation.  The model parameters are set to the default values."])
table.add_row(["1", "None", "Invalid combination."])
table.add_row(["n", "None", "This case is used to set the model parameters prior to minimisation or calculation.  The length of the val array must be equal to the number of model parameters.  The parameters will be set to the corresponding number."])
table.add_row(["None", "1", "The parameter matching the string will be set to the default value."])
table.add_row(["1", "1", "The parameter matching the string will be set to the supplied number."])
table.add_row(["n", "1", "Invalid combination."])
table.add_row(["None", "n", "Each parameter matching the strings will be set to the default values."])
table.add_row(["1", "n", "Each parameter matching the strings will be set to the supplied number."])
table.add_row(["n", "n", "Each parameter matching the strings will be set to the corresponding number.  Both arrays must be of equal length."])
uf.desc[-1].add_table(table.label)
# Spin identification.
uf.desc.append(Desc_container("Spin identification"))
uf.desc[-1].add_paragraph("If the spin ID is left unset, then this will be applied to all spins.  If the data is global non-spin specific data, such as diffusion tensor parameters, supplying the spin identifier will terminate the program with an error.")
uf.desc.append(regexp_doc)
uf.desc.append(Model_free.set_doc)
uf.desc.append(Model_free.return_data_name_doc)
uf.desc.append(Model_free.default_value_doc)
uf.desc.append(diffusion_tensor.__set_doc__)
uf.desc.append(diffusion_tensor.__return_data_name_doc__)
uf.desc.append(diffusion_tensor.__default_value_doc__)
uf.desc.append(Jw_mapping.set_doc)
uf.desc.append(Jw_mapping.return_data_name_doc)
uf.desc.append(Jw_mapping.default_value_doc)
uf.desc.append(Consistency_tests.set_doc)
uf.desc.append(Consistency_tests.return_data_name_doc)
uf.desc.append(Consistency_tests.default_value_doc)
uf.desc.append(Relax_fit.set_doc)
uf.desc.append(Relax_fit.return_data_name_doc)
uf.desc.append(Relax_fit.default_value_doc)
uf.desc.append(N_state_model.set_doc)
uf.desc.append(N_state_model.return_data_name_doc)
uf.desc.append(N_state_model.default_value_doc)
uf.desc.append(Relax_disp.set_doc)
uf.desc.append(Relax_disp.return_data_name_doc)
uf.desc.append(Relax_disp.default_value_doc)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To set the parameter values for the current data pipe to the default values, for all spins, type:")
uf.desc[-1].add_prompt("relax> value.set()")
uf.desc[-1].add_paragraph("To set the parameter values of residue 10, which is in the current model-free data pipe 'm4' and has the parameters {S2, te, Rex}, the following can be used.  Rex term is the value for the first given field strength.")
uf.desc[-1].add_prompt("relax> value.set([0.97, 2.048*1e-9, 0.149], spin_id=':10')")
uf.desc[-1].add_prompt("relax> value.set(val=[0.97, 2.048*1e-9, 0.149], spin_id=':10')")
uf.desc[-1].add_paragraph("To set the CSA value of all spins to the default value, type:")
uf.desc[-1].add_prompt("relax> value.set(param='csa')")
uf.desc[-1].add_paragraph("To set the CSA value of all spins to -172 ppm, type:")
uf.desc[-1].add_prompt("relax> value.set(-172 * 1e-6, 'csa')")
uf.desc[-1].add_prompt("relax> value.set(val=-172 * 1e-6, param='csa')")
uf.desc[-1].add_paragraph("To set the NH bond length of all spins to 1.02 Angstroms, type:")
uf.desc[-1].add_prompt("relax> value.set(1.02 * 1e-10, 'r')")
uf.desc[-1].add_prompt("relax> value.set(val=1.02 * 1e-10, param='r')")
uf.desc[-1].add_paragraph("To set both the bond length and the CSA value to the default values, type:")
uf.desc[-1].add_prompt("relax> value.set(param=['r', 'csa'])")
uf.desc[-1].add_paragraph("To set both tf and ts to 100 ps, type:")
uf.desc[-1].add_prompt("relax> value.set(100e-12, ['tf', 'ts'])")
uf.desc[-1].add_prompt("relax> value.set(val=100e-12, param=['tf', 'ts'])")
uf.desc[-1].add_paragraph("To set the S2 and te parameter values of residue 126, Ca spins to 0.56 and 13 ps, type:")
uf.desc[-1].add_prompt("relax> value.set([0.56, 13e-12], ['s2', 'te'], ':126@Ca')")
uf.desc[-1].add_prompt("relax> value.set(val=[0.56, 13e-12], param=['s2', 'te'], spin_id=':126@Ca')")
uf.desc[-1].add_prompt("relax> value.set(val=[0.56, 13e-12], param=['s2', 'te'], spin_id=':126@Ca')")
uf.backend = value.set
uf.menu_text = "&set"
uf.wizard_height_desc = 480
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'value' + sep + 'value.png'


# The value.write user function.
uf = uf_info.add_uf('value.write')
uf.title = "Write spin specific data values to a file."
uf.title_short = "Value writing."
uf.add_keyarg(
    name = "param",
    py_type = "str",
    desc_short = "parameter",
    desc = "The parameter.",
    wiz_element_type = 'combo',
    wiz_combo_iter = value.get_parameters,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file.",
    wiz_filesel_style = FD_SAVE
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
    name = "scaling",
    default = 1.0,
    py_type = "float",
    desc_short = "scaling",
    desc = "The factor to scale parameters by."
)
uf.add_keyarg(
    name = "comment",
    py_type = "str",
    desc_short = "comment",
    desc = "Text which will be added to the start of the file as comments.  All lines will be prefixed by '# '.",
    can_be_none = True
)
uf.add_keyarg(
    name = "bc",
    default = False,
    py_type = "bool",
    desc_short = "back calculated value flag",
    desc = "A flag which if True will cause the back calculated values to be written to file rather than the actual data."
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which, if set to True, will cause the file to be overwritten."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The values corresponding to the given parameter will be written to file.  The scaling argument can be used to scale the parameter values.  This can be useful for example in the case of the model-free Rex parameter to obtain the spectrometer dependent value from the omega_ex field strength independent internal value.  Or to scale correlation times from seconds down to nanosecond or picosecond timescales.")
uf.desc.append(regexp_doc)
uf.desc.append(Model_free.return_data_name_doc)
uf.desc.append(Model_free.write_doc)
uf.desc.append(Jw_mapping.return_data_name_doc)
uf.desc.append(Consistency_tests.return_data_name_doc)
uf.desc.append(Noe.return_data_name_doc)
uf.desc.append(Relax_fit.return_data_name_doc)
uf.desc.append(N_state_model.return_data_name_doc)
uf.desc.append(Relax_disp.return_data_name_doc)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To write the CSA values to the file 'csa.txt', type one of:")
uf.desc[-1].add_prompt("relax> value.write('csa', 'csa.txt')")
uf.desc[-1].add_prompt("relax> value.write(param='csa', file='csa.txt')")
uf.desc[-1].add_paragraph("To write the NOE values to the file 'noe', type one of:")
uf.desc[-1].add_prompt("relax> value.write('noe', 'noe.out')")
uf.desc[-1].add_prompt("relax> value.write(param='noe', file='noe.out')")
uf.desc[-1].add_prompt("relax> value.write(param='noe', file='noe.out')")
uf.desc[-1].add_prompt("relax> value.write(param='noe', file='noe.out', force=True)")
uf.desc[-1].add_paragraph("To write the model-free Rex values scaled to 600 MHz to the file 'rex_600', type one of:")
uf.desc[-1].add_prompt("relax> value.write('rex', 'rex_600', scaling=(2.0*pi*600e6)**2)")
uf.desc[-1].add_prompt("relax> value.write(param='rex', file='rex_600', scaling=(2.0*pi*600e6)**2)")
uf.backend = value.write
uf.menu_text = "&write"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_height_desc = 400
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'value' + sep + 'value.png'
