###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""The dx user function definitions for controlling the OpenDX visualisation software."""

# Python module imports.
import dep_check
if dep_check.wx_module:
    from wx import FD_OPEN
else:
    FD_OPEN = -1

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from lib.software.opendx.execute import run
from pipe_control.opendx import map
from specific_analyses.frame_order.parameter_object import Frame_order_params; frame_order_params = Frame_order_params()
from specific_analyses.model_free.parameter_object import Model_free_params; model_free_params = Model_free_params()
from specific_analyses.n_state_model.parameter_object import N_state_params; n_state_params = N_state_params()
from specific_analyses.relax_disp.parameter_object import Relax_disp_params; relax_disp_params = Relax_disp_params()
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class("dx")
uf_class.title = "Class for interfacing with OpenDX."
uf_class.menu_text = "&dx"
uf_class.gui_icon = "relax.opendx"


# The dx.execute user function.
uf = uf_info.add_uf("dx.execute")
uf.title = "Execute an OpenDX program."
uf.title_short = "OpenDX execution."
uf.add_keyarg(
    name = "file_prefix",
    default = "map",
    py_type = "str",
    desc_short = "file name",
    desc = "The file name prefix.  For example if file is set to 'temp', then the OpenDX program temp.net will be loaded."
)
uf.add_keyarg(
    name = "dir",
    default = "dx",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory to change to for running OpenDX.  If this is set to None, OpenDX will be run in the current directory.",
    can_be_none = True
)
uf.add_keyarg(
    name = "dx_exe",
    default = "dx",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "OpenDX executable file name",
    desc = "The OpenDX executable file.",
    wiz_filesel_style = FD_OPEN,
    wiz_filesel_preview = False
)
uf.add_keyarg(
    name = "vp_exec",
    default = True,
    py_type = "bool",
    desc_short = "visual program execution flag",
    desc = "A flag specifying whether to execute the visual program automatically at start-up.  The default of True causes the program to be executed."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will execute OpenDX to display the space maps created previously by the dx.map user function.  This will work for any type of OpenDX map.")
uf.backend = run
uf.menu_text = "&execute"
uf.gui_icon = "oxygen.categories.applications-education"
uf.wizard_size = (700, 500)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'opendx.png'


# The dx.map user function.
uf = uf_info.add_uf("dx.map")
uf.title = "Create a map of the given space in OpenDX format."
uf.title_short = "OpenDX map creation."
uf.display = True
uf.add_keyarg(
    name = "params",
    py_type = "str_list",
    desc_short = "parameters",
    desc = "The parameters to be mapped.  This should be an array of strings, the meanings of which are described below."
)
uf.add_keyarg(
    name = "map_type",
    default = "Iso3D",
    py_type = "str",
    desc_short = "map type",
    desc = "The type of map to create.  For example the default, a 3D isosurface, the type is 'Iso3D'.  See below for more details.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["Iso3D"],
    wiz_read_only = True,
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin ID string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "inc",
    default = 20,
    py_type = "int",
    desc_short = "number of increments",
    desc = "The number of increments to map in each dimension.  This value controls the resolution of the map.",
    wiz_element_type = "spin"
)
uf.add_keyarg(
    name = "lower",
    py_type = "num_list",
    desc_short = "lower bounds",
    desc = "The lower bounds of the space.  If you wish to change the lower bounds of the map then supply an array of length equal to the number of parameters in the model.  A lower bound for each parameter must be supplied.  If nothing is supplied then the defaults will be used.",
    can_be_none = True
)
uf.add_keyarg(
    name = "upper",
    py_type = "num_list",
    desc_short = "upper bounds",
    desc = "The upper bounds of the space.  If you wish to change the upper bounds of the map then supply an array of length equal to the number of parameters in the model.  A upper bound for each parameter must be supplied.  If nothing is supplied then the defaults will be used.",
    can_be_none = True
)
uf.add_keyarg(
    name = "axis_incs",
    default = 5,
    py_type = "int",
    desc_short = "axis increments",
    desc = "The number of increments or ticks displaying parameter values along the axes of the OpenDX plot.",
    wiz_element_type = "spin"
)
uf.add_keyarg(
    name = "file_prefix",
    default = "map",
    py_type = "str",
    desc_short = "file prefix",
    desc = "The file name.  All the output files are prefixed with this name.  The main file containing the data points will be called the value of 'file'.  The OpenDX program will be called 'file.net' and the OpenDX import file will be called 'file.general'."
)
uf.add_keyarg(
    name = "dir",
    default = "dx",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory to output files to.  Set this to 'None' if you do not want the files to be placed in subdirectory.  If the directory does not exist, it will be created.",
    can_be_none = True
)
uf.add_keyarg(
    name = "point",
    py_type = "list_val_or_list_of_list_val",
    dim = (None, 3),
    desc_short = "highlight points in the space",
    desc = "This argument allows specific points in the optimisation space to be displayed as coloured spheres.  This can be used to highlight a minimum or other any other feature of the space.  Either a single point or a list of points can be supplied.  Each point is a list of floating point numbers in the form [x, y, z]",
    list_titles = ['X coordinate', 'Y coordinate', 'Z coordinate'],
    can_be_none = True
)
uf.add_keyarg(
    name = "point_file",
    default = "point",
    py_type = "str",
    desc_short = "point file name prefix",
    desc = "The name of that the point output files will be prefixed with.",
    can_be_none = True
)
uf.add_keyarg(
    name = "chi_surface",
    default = None,
    py_type = "float_array",
    desc_short = "Set the chi2 surface level for the Innermost, Inner, Middle and Outer Isosurface.",
    desc = "A list of 4 numbers, setting the level for the 4 isosurfaces. Useful in scripting if you create a set of OpenDX maps with all the same contour levels.  Ideal for comparisons.",
    can_be_none = True,
    dim = 4
)
uf.add_keyarg(
    name = "create_par_file",
    default = False,
    py_type = "bool",
    desc_short = "creation of file with parameter and calculated chi2",
    desc = "A flag specifying whether to create a file with parameters and associated chi2 value.  The default of False causes the file not to be created."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will map the space corresponding to the spin identifier and create the OpenDX files.  The map type can be changed to one of the following supported map types:")
table = uf_tables.add_table(label="table: opendx map", caption="OpenDx mapping types.")
table.add_headings(["Surface type", "Name"])
table.add_row(["3D isosurface", "'Iso3D'"])
uf.desc[-1].add_table(table.label)
# Additional.
uf.desc.append(model_free_params.uf_doc(label="table: all model-free parameters"))
uf.desc.append(n_state_params.uf_doc(label="table: N-state parameters"))
uf.desc.append(relax_disp_params.uf_doc(label="table: dispersion parameters"))
uf.desc.append(frame_order_params.uf_doc(label="table: frame order parameters"))
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following commands will generate a map of the extended model-free space for model 'm5' consisting of the parameters {S2, S2f, ts}.  Files will be output into the directory 'dx' and will be prefixed by 'map'.  In this case, the system is a protein and residue number 6 will be mapped.")
uf.desc[-1].add_prompt("relax> dx.map(['s2', 's2f', 'ts'], spin_id=':6')")
uf.desc[-1].add_prompt("relax> dx.map(['s2', 's2f', 'ts'], spin_id=':6', file_prefix='map', dir='dx')")
uf.desc[-1].add_prompt("relax> dx.map(params=['s2', 's2f', 'ts'], spin_id=':6', inc=20, file_prefix='map', dir='dx')")
uf.desc[-1].add_prompt("relax> dx.map(params=['s2', 's2f', 'ts'], spin_id=':6', map_type='Iso3D', inc=20, file_prefix='map', dir='dx')")
uf.desc[-1].add_paragraph("To map the model-free space 'm4' for residue 2, spin N6 defined by the parameters {S2, te, Rex}, name the results 'test', and to place the files in the current directory, use one of the following commands:")
uf.desc[-1].add_prompt("relax> dx.map(['s2', 'te', 'rex'], spin_id=':2@N6', file_prefix='test', dir=None)")
uf.desc[-1].add_prompt("relax> dx.map(params=['s2', 'te', 'rex'], spin_id=':2@N6', inc=100, file_prefix='test', dir=None)")
uf.backend = map
uf.menu_text = "&map"
uf.gui_icon = "relax.grid_search"
uf.wizard_height_desc = 280
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'opendx.png'
