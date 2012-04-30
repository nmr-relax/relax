###############################################################################
#                                                                             #
# Copyright (C) 2011-2012 Edward d'Auvergne                                   #
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
"""Module containing the Bruker Dynamics Centre user function class."""
__docformat__ = 'plaintext'

# relax module imports.
import arg_check
from base_class import User_fn_class
from generic_fns import bruker


class Bruker(User_fn_class):
    """Class containing the function for reading the Bruker Dynamics Centre (DC) files."""

    def read(self, ri_id=None, file=None, dir=None):
        """Read the Bruker Dynamics Centre (DC) file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        ri_id:  The relaxation data ID string.

        file:  The name of the DC file.

        dir:  The directory where the file is located.


        Description
        ~~~~~~~~~~~

        This user function is used to load all of the data out of a Bruker DC file for subsequent
        analysis within relax.
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "bruker.read("
            text = text + "ri_id=" + repr(ri_id)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(ri_id, 'relaxation data ID string')
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)

        # Execute the functional code.
        bruker.read(ri_id=ri_id, file=file, dir=dir)
