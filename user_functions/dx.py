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
"""Module containing the 'dx' user function data for controlling the OpenDX visualisation software."""

# relax module imports.
from generic_fns import diffusion_tensor
from graphics import WIZARD_IMAGE_PATH
import opendx.main
from prompt.doc_string import docs
from specific_fns.model_free import Model_free
from user_functions.data import Uf_info; uf_info = Uf_info()


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
    desc_short = "OpenDX executable file name",
    desc = "The OpenDX executable file."
)
uf.add_keyarg(
    name = "vp_exec",
    default = True,
    py_type = "bool",
    desc_short = "visual program execution flag",
    desc = "A flag specifying whether to execute the visual program automatically at start-up.  The default of True causes the program to be executed."
)
uf.desc = """
This will execute OpenDX to display the space maps created previously by the dx.map user function.  This will work for any type of OpenDX map.
"""
uf.backend = opendx.main.run
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
    desc = "The parameters to be mapped.  This argument should be an array of strings, the meanings of which are described below."
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
    py_type = "num_list",
    desc_short = "point",
    desc = "An array of parameter values where a point in the map, shown as a red sphere, will be placed.  The length must be equal to the number of parameters.",
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
    name = "remap",
    py_type = "func",
    arg_type = "func",
    desc_short = "remap function",
    desc = "A user supplied remapping function.  This function will receive the parameter array and must return an array of equal length.",
    can_be_none = True
)
uf.desc = """
This will map the space corresponding to the spin identifier and create the OpenDX files.  The map type can be changed to one of the following supported map types:
_____________________________________________________________________________
|                                           |                               |
| Surface type                              | Name                          |
|___________________________________________|_______________________________|
|                                           |                               |
| 3D isosurface                             | 'Iso3D'                       |
|___________________________________________|_______________________________|
"""
uf.additional = [
    docs.regexp.doc,
    diffusion_tensor.__return_data_name_prompt_doc__,
    Model_free.return_data_name_doc
]
uf.prompt_examples = """
The following commands will generate a map of the extended model-free space for model 'm5'
consisting of the parameters {S2, S2f, ts}.  Files will be output into the
directory 'dx' and will be prefixed by 'map'.  In this case, the system is a protein and
residue number 6 will be mapped.

relax> dx.map(['s2', 's2f', 'ts'], spin_id=':6')
relax> dx.map(['s2', 's2f', 'ts'], spin_id=':6', file_prefix='map', dir='dx')
relax> dx.map(params=['s2', 's2f', 'ts'], spin_id=':6', inc=20, file_prefix='map', dir='dx')
relax> dx.map(params=['s2', 's2f', 'ts'], spin_id=':6', map_type='Iso3D', inc=20,
              file_prefix='map', dir='dx')


To map the model-free space 'm4' for residue 2, spin N6 defined by the parameters {S2, te,
Rex}, name the results 'test', and to place the files in the current directory, use one of
the following commands:

relax> dx.map(['s2', 'te', 'rex'], spin_id=':2@N6', file_prefix='test', dir=None)
relax> dx.map(params=['s2', 'te', 'rex'], spin_id=':2@N6', inc=100, file_prefix='test', dir=None)
"""
uf.backend = opendx.main.map
uf.menu_text = "&map"
uf.gui_icon = "relax.grid_search"
uf.wizard_size = (1000, 800)
uf.wizard_image = WIZARD_IMAGE_PATH + 'opendx.png'
