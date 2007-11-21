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


class Align_tensor:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the alignment tensor."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def init(self, params=None, param_types=0, errors=0):
        """Function for initialising the alignment tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        params:  The alignment tensor data.

        param_types:  A flag to select different parameter combinations.

        errors:  A flag which determines if the alignment tensor data or its errors are being input.


        Description
        ~~~~~~~~~~~

        Using this function, the alignment tensor data can be set up.  The params argument should be
        a tuple of floating point numbers (a list surrounded by round brakets).  These correspond to
        the parameters of the tensor, which can be specified by the param_types argument, where the
        values correspond to

            0:  (Szz, Sxx-yy, Sxy, Sxz, Syz)  (in units of Hertz),

        (other formats may be implemented later).


        Examples
        ~~~~~~~~

        To set a rhombic tensor to the run 'CaM', type one of:

        relax> align_tensor.init((-8.6322e-05, -5.5786e-04, -3.1732e-05, 2.2927e-05, 2.8599e-04))
        relax> align_tensor.init((-8.6322e-05, -5.5786e-04, -3.1732e-05, 2.2927e-05, 2.8599e-04), 0)
        relax> align_tensor.init(params=(-8.6322e-05, -5.5786e-04, -3.1732e-05, 2.2927e-05,
                                 2.8599e-04))
        relax> align_tensor.init(params=(-8.6322e-05, -5.5786e-04, -3.1732e-05, 2.2927e-05,
                                 2.8599e-04), param_types=0)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "align_tensor.init("
            text = text + "params=" + `params`
            text = text + ", param_types=" + `param_types`
            text = text + ", errors=" + `errors` + ")"
            print text

        # Parameter argument.
        if type(params) != int and type(params) != float and type(params) != tuple:
            raise RelaxNumTupleError, ('diffusion parameters', params)
        if type(params) == tuple:
            if len(params) != 4 and len(params) != 6:
                raise RelaxError, "The diffusion parameters argument must either be a number or a tuple of numbers of length 4 or 6."
            for i in xrange(len(params)):
                if type(params[i]) != float and type(params[i]) != int:
                    raise RelaxNumTupleError, ('diffusion parameters', params)

        # Parameter types argument.
        if type(param_types) != int:
            raise RelaxIntError, ('parameter types', param_types)

        # The errors flag.
        if type(errors) != int or (errors != 0 and errors != 1):
            raise RelaxBinError, ('errors flag', errors)

        # Execute the functional code.
        align_tensor.init(params=params, param_types=param_types, errors=errors)
