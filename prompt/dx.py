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
"""Module containing the 'dx' user function class for controlling the OpenDX visualisation software."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class, _build_doc
import arg_check
from doc_string import docs
from generic_fns import diffusion_tensor
import opendx.main
from relax_errors import RelaxError
from specific_fns.model_free import Model_free
from status import Status; status = Status()


class OpenDX(User_fn_class):
    """Class for interfacing with OpenDX."""

    def execute(self, file="map", dir="dx", dx_exe="dx", vp_exec=True):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "dx("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", dx_exe=" + repr(dx_exe)
            text = text + ", vp_exec=" + repr(vp_exec) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_str(dx_exe, 'OpenDX executable file name')
        arg_check.is_bool(vp_exec, 'visual program execution flag')

        # Execute the functional code.
        opendx.main.run(file_prefix=file, dir=dir, dx_exe=dx_exe, vp_exec=vp_exec)

    # The function doc info.
    execute._doc_title = "Execution of OpenDX."
    execute._doc_title_short = "OpenDX execution."
    execute._doc_args = [
        ["file", "The file name prefix.  For example if file is set to 'temp', then the OpenDX program temp.net will be loaded."],
        ["dir", "The directory to change to for running OpenDX.  If this is set to None, OpenDX will be run in the current directory."],
        ["dx_exe", "The OpenDX executable file."],
        ["vp_exec", "A flag specifying whether to execute the visual program automatically at start-up.  The default of True causes the program to be executed."]
    ]
    _build_doc(execute)


    def map(self, params=None, map_type="Iso3D", spin_id=None, inc=20, lower=None, upper=None, axis_incs=5, file_prefix="map", dir="dx", point=None, point_file="point", remap=None):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "map("
            text = text + "params=" + repr(params)
            text = text + ", map_type=" + repr(map_type)
            text = text + ", spin_id=" + repr(spin_id)
            text = text + ", inc=" + repr(inc)
            text = text + ", lower=" + repr(lower)
            text = text + ", upper=" + repr(upper)
            text = text + ", axis_incs=" + repr(axis_incs)
            text = text + ", file_prefix=" + repr(file_prefix)
            text = text + ", dir=" + repr(dir)
            text = text + ", point=" + repr(point)
            text = text + ", point_file=" + repr(point_file)
            text = text + ", remap=" + repr(remap) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str_list(params, 'parameters')
        arg_check.is_str(map_type, 'map type')
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)
        arg_check.is_int(inc, 'increment')
        if inc <= 1:
            raise RelaxError("The increment value needs to be greater than 1.")
        arg_check.is_num_list(lower, 'lower bounds', size=len(params), can_be_none=True)
        arg_check.is_num_list(upper, 'upper bounds', size=len(params), can_be_none=True)
        arg_check.is_int(axis_incs, 'axis increments')
        if axis_incs <= 1:
            raise RelaxError("The axis increment value needs to be greater than 1.")
        arg_check.is_str(file_prefix, 'file prefix')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_num_list(point, 'point', size=len(params), can_be_none=True)
        if point != None:
            arg_check.is_str(point_file, 'point file name')
        arg_check.is_func(remap, 'remap function', can_be_none=True)

        # Execute the functional code.
        opendx.main.map(params=params, map_type=map_type, spin_id=spin_id, inc=inc, lower=lower, upper=upper, axis_incs=axis_incs, file_prefix=file_prefix, dir=dir, point=point, point_file=point_file, remap=remap)

    # The function doc info.
    map._doc_title = "Create a map of the given space in OpenDX format."
    map._doc_title_short = "OpenDX map creation."
    map._doc_args = [
        ["params", "The parameters to be mapped.  This argument should be an array of strings, the meanings of which are described below."],
        ["map_type", "The type of map to create.  For example the default, a 3D isosurface, the type is 'Iso3D'.  See below for more details."],
        ["spin_id", "The spin identification numbe."],
        ["inc", "The number of increments to map in each dimension.  This value controls the resolution of the map."],
        ["lower", "The lower bounds of the space.  If you wish to change the lower bounds of the map then supply an array of length equal to the number of parameters in the model.  A lower bound for each parameter must be supplied.  If nothing is supplied then the defaults will be used."],
        ["upper", "The upper bounds of the space.  If you wish to change the upper bounds of the map then supply an array of length equal to the number of parameters in the model.  A upper bound for each parameter must be supplied.  If nothing is supplied then the defaults will be used."],
        ["axis_incs", "The number of increments or ticks displaying parameter values along the axes of the OpenDX plot."],
        ["file_prefix", "The file name.  All the output files are prefixed with this name.  The main file containing the data points will be called the value of 'file'.  The OpenDX program will be called 'file.net' and the OpenDX import file will be called 'file.general'."],
        ["dir", "The directory to output files to.  Set this to 'None' if you do not want the files to be placed in subdirectory.  If the directory does not exist, it will be created."],
        ["point", "An array of parameter values where a point in the map, shown as a red sphere, will be placed.  The length must be equal to the number of parameters."],
        ["point_file", "The name of that the point output files will be prefixed with."],
        ["remap", "A user supplied remapping function.  This function will receive the parameter array and must return an array of equal length."]
    ]
    map._doc_desc = """
        The map type can be changed to one of the following supported map types:
        _____________________________________________________________________________
        |                                           |                               |
        | Surface type                              | Name                          |
        |___________________________________________|_______________________________|
        |                                           |                               |
        | 3D isosurface                             | 'Iso3D'                       |
        |___________________________________________|_______________________________|
        """
    map._doc_examples = """
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
    map._doc_additional = [
        docs.regexp.doc,
        diffusion_tensor.__return_data_name_prompt_doc__,
        Model_free.return_data_name_doc
    ]
    _build_doc(map)
