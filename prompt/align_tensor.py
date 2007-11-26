###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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

# Python module imports.
import sys

# relax module imports.
import help
from generic_fns import align_tensor
from relax_errors import RelaxError, RelaxBinError, RelaxFloatError, RelaxIntError, RelaxNoneStrError, RelaxNumTupleError, RelaxStrError


class Align_tensor:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the alignment tensor."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def copy(self, pipe_from=None, pipe_to=None):
        """Function for copying alignment tensor data from one data pipe to another.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The name of the data pipe to copy the alignment tensor data from.

        pipe_to:  The name of the data pipe to copy the alignment tensor data to.


        Description
        ~~~~~~~~~~~

        This function will copy the alignment tensor data between data pipes.  The destination data
        pipe must not contain any alignment tensor data.  If the pipe_from or pipe_to arguments are
        not supplied, then both will default to the current data pipe (hence giving one argument is
        essential).


        Examples
        ~~~~~~~~

        To copy the alignment tensor from the data pipe 'Pf1' to the current data pipe, type:

        relax> align_tensor.copy('Pf1')
        relax> align_tensor.copy(pipe_from='Pf1')


        To copy the alignment tensor from the current data pipe to the data pipe 'Otting', type:

        relax> align_tensor.copy(pipe_to='Otting')


        To copy the alignment tensor from the data pipe 'Pf1' to 'Otting', type:

        relax> align_tensor.copy('Pf1', 'Otting')
        relax> align_tensor.copy(pipe_from='Pf1', pipe_to='Otting')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "align_tensor.copy("
            text = text + "pipe_from=" + `pipe_from`
            text = text + ", pipe_to=" + `pipe_to` + ")"
            print text

        # The pipe_from argument.
        if pipe_from != None and type(pipe_from) != str:
            raise RelaxNoneStrError, ('pipe from', pipe_from)

        # The pipe_to argument.
        if pipe_to != None and type(pipe_to) != str:
            raise RelaxNoneStrError, ('pipe to', pipe_to)

        # Both pipe arguments cannot be None.
        if pipe_from == None and pipe_to == None:
            raise RelaxError, "The pipe_from and pipe_to arguments cannot both be set to None."

        # Execute the functional code.
        align_tensor.copy(pipe_from=pipe_from, pipe_to=pipe_to)


    def delete(self):
        """Function for deleting alignment tensor data.

        Description
        ~~~~~~~~~~~

        This function will delete all alignment tensor data from the current data pipe.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "align_tensor.delete()"
            print text

        # Execute the functional code.
        align_tensor.delete()


    def display(self):
        """Function for displaying the alignment tensor information."""

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "align_tensor.display()"
            print text

        # Execute the functional code.
        align_tensor.display()


    def init(self, params=None, scale=1.0, angle_units='deg', param_types=0, errors=0):
        """Function for initialising the alignment tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        params:  The alignment tensor data.

        scale:  The alignment tensor eigenvalue scaling value.

        angle_units:  The units for the angle parameters.

        param_types:  A flag to select different parameter combinations.

        errors:  A flag which determines if the alignment tensor data or its errors are being input.


        Description
        ~~~~~~~~~~~

        Using this function, the alignment tensor data can be set up.  The params argument should be
        a tuple of floating point numbers (a list surrounded by round brakets).  These correspond to
        the parameters of the tensor, which can be specified by the param_types argument, where the
        values correspond to

            0:  (Axx, Ayy, Axy, Axz, Ayz)  (in units of Hertz),
            1:  (Azz, Axx-yy, Axy, Axz, Ayz)  (Pales format in units of Hertz),

        (other formats may be implemented later).


        Examples
        ~~~~~~~~

        To set a rhombic tensor to the run 'CaM', type one of:

        relax> align_tensor.init((-8.6322e-05, -5.5786e-04, -3.1732e-05, 2.2927e-05, 2.8599e-04),
                                 param_types=1)
        relax> align_tensor.init((-8.6322e-05, -5.5786e-04, -3.1732e-05, 2.2927e-05, 2.8599e-04),
                                 param_types=1)
        relax> align_tensor.init(params=(-8.6322e-05, -5.5786e-04, -3.1732e-05, 2.2927e-05,
                                 2.8599e-04), param_types=1)
        relax> align_tensor.init(params=(-8.6322e-05, -5.5786e-04, -3.1732e-05, 2.2927e-05,
                                 2.8599e-04), param_types=1)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "align_tensor.init("
            text = text + "params=" + `params`
            text = text + ", scale=" + `scale`
            text = text + ", angle_units=" + `angle_units`
            text = text + ", param_types=" + `param_types`
            text = text + ", errors=" + `errors` + ")"
            print text

        # Parameter argument.
        if type(params) != tuple:
            raise RelaxNumTupleError, ('alignment tensor parameters', params)
        else:
            if len(params) != 5:
                raise RelaxError, "The alignment tensor parameters argument must be a tuple of numbers of length 5."
            for i in xrange(len(params)):
                if type(params[i]) != float and type(params[i]) != int:
                    raise RelaxNumTupleError, ('alignment tensor parameters', params)

        # Scale argument.
        if type(scale) != float:
            raise RelaxFloatError, ('scale', scale)

        # Angle units argument.
        if type(angle_units) != str:
            raise RelaxStrError, ('angle units', angle_units)

        # Parameter types argument.
        if type(param_types) != int:
            raise RelaxIntError, ('parameter types', param_types)

        # The errors flag.
        if type(errors) != int or (errors != 0 and errors != 1):
            raise RelaxBinError, ('errors flag', errors)

        # Execute the functional code.
        align_tensor.init(params=params, scale=scale, angle_units=angle_units, param_types=param_types, errors=errors)
