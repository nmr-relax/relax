###############################################################################
#                                                                             #
# Copyright (C) 2004-2008 Edward d'Auvergne                                   #
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
"""Module containing the 'noe' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
import help
from relax_errors import RelaxStrError
from specific_fns.setup import noe_obj


class Noe:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for calculating NOE data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def spectrum_type(self, spectrum_type=None, spectrum_id=None):
        """Function for setting the spectrum type for pre-loaded peak intensities.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spectrum_type:  The type of NOE spectrum, one of 'ref' or 'sat'.

        spectrum_id:  The spectrum identification string.


        Description
        ~~~~~~~~~~~

        The spectrum_type argument can have the following values:
            'ref':  The NOE reference spectrum.
            'sat':  The NOE spectrum with proton saturation turned on.

        Peak intensities should be loaded before calling this user function via the
        'spectrum.read_intensities()' user function.  The intensity values will then be associated
        with a spectrum identifier which can be used here.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "noe.spectrum_type("
            text = text + "spectrum_type=" + `spectrum_type`
            text = text + ", spectrum_id=" + `spectrum_id` + ")"
            print text

        # The spectrum type.
        if type(spectrum_type) != str:
            raise RelaxStrError, ('spectrum type', spectrum_type)

        # The spectrum identification string.
        if type(spectrum_id) != str:
            raise RelaxStrError, ('spectrum identification string', spectrum_id)

        # Execute the functional code.
        noe_obj.spectrum_type(spectrum_type=spectrum_type, spectrum_id=spectrum_id)
