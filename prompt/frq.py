###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
"""User functions for manipulating spectrometer frequencies."""

# Python module imports.
import sys

# relax module imports.
import help
from relax_errors import RelaxNumError, RelaxStrError
import generic_fns.frq


class Frq:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating spectrometer frequencies."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def set(self, id=None, frq=None):
        """Set the spectrometer frequency of the experiment.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        id:  The experiment identification string.

        frq:  The spectrometer frequency in Hertz.


        Description
        ~~~~~~~~~~~

        This user function allows the spectrometer frequency of a given experiment to be set.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "frq("
            text = text + "id=" + `id`
            text = text + ", frq=" + `frq` + ")"
            print text

        # Id string.
        if type(id) != str:
            raise RelaxStrError, ('experiment identification string', id)

        # The spectrometer frequency.
        if type(frq) != float and type(frq) != int:
            raise RelaxNumError, ('spectrometer frequency', frq)

        # Execute the functional code.
        generic_fns.frq.set(id=id, frq=frq)
