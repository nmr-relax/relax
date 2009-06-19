###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
"""Module containing the user function class of the Frame Order theories."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
import help
from specific_fns.setup import frame_order_obj
from relax_errors import RelaxStrError


class Frame_order:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class containing the user functions of the Frame Order theories."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def select_model(self, model=None):
        """Select and set up the Frame Order model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the preset Frame Order model.


        Description
        ~~~~~~~~~~~

        Prior to optimisation, the Frame Order model should be selected.  The list of available
        models are:

        'iso cone' - The isotropic cone model.


        Examples
        ~~~~~~~~

        To select the isotropic cone model, type:

        relax> frame_order.select_model(model='iso cone')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "frame_order.select_model("
            text = text + "model=" + `model` + ")"
            print text

        # Model argument.
        if type(model) != str:
            raise RelaxStrError, ('model', model)

        # Execute the functional code.
        frame_order_obj.select_model(model=model)
