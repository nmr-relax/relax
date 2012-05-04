###############################################################################
#                                                                             #
# Copyright (C) 2008-2012 Edward d'Auvergne                                   #
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
"""Module containing the 'frq' user function class for manipulating spectrometer frequencies."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
import generic_fns.frq
from status import Status; status = Status()


class Frq(User_fn_class):
    """Class for manipulating spectrometer frequencies."""

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
        if status.prompt_intro:
            text = status.ps3 + "frq("
            text = text + "id=" + repr(id)
            text = text + ", frq=" + repr(frq) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(id, 'experiment identification string')
        arg_check.is_num(frq, 'spectrometer frequency')

        # Execute the functional code.
        generic_fns.frq.set(id=id, frq=frq)
