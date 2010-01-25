###############################################################################
#                                                                             #
# Copyright (C) 2004-2005, 2009-2010 Edward d'Auvergne                        #
# Copyright (C) 2007-2008 Sebastien Morin                                     #
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
"""Module containing the 'consistency_tests' user function class."""
__docformat__ = 'plaintext'

# Python module imports.

# relax module imports.
from base_class import User_fn_class
import arg_check
from specific_fns.setup import consistency_tests_obj


class Consistency_tests(User_fn_class):
    """Class containing functions specific to consistency tests for datasets from different fields."""

    def set_frq(self, frq=None):
        """Function for selecting which relaxation data to use in the consistency tests.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        frq:  The spectrometer frequency in Hz.


        Description
        ~~~~~~~~~~~

        This function will select the relaxation data to use in the consistency tests corresponding
        to the given frequencies.


        Examples
        ~~~~~~~~

        relax> consistency_tests.set_frq(600.0 * 1e6)
        relax> consistency_tests.set_frq(frq=600.0 * 1e6)
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "consistency_tests.set_frq("
            text = text + "frq=" + repr(frq) + ")"
            print(text)

        # The argument checks.
        arg_check.is_num(frq, 'spectrometer frequency')

        # Execute the functional code.
        consistency_tests_obj._set_frq(frq=frq)
