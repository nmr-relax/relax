###############################################################################
#                                                                             #
# Copyright (C) 2003-2005,2008-2009 Edward d'Auvergne                         #
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
"""Module containing the BMRB user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
from base_class import User_fn_class
import check
from generic_fns import bmrb
from relax_errors import RelaxBoolError, RelaxIntError, RelaxNoneStrError, RelaxStrError, RelaxStrFileError


class BMRB(User_fn_class):
    """Class for interfacing with the BMRB (http://www.bmrb.wisc.edu/)."""

    def display(self, version='3.1'):
        """Display the BMRB data in NMR-STAR format."""

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "bmrb.display("
            text = text + "version=" + repr(version) + ")"
            print(text)

        # Execute the functional code.
        bmrb.display(version=version)


    def read(self, file=None, dir=None, version='3.1'):
        """Read BMRB files in the NMR-STAR format.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the BMRB STAR formatted file.

        dir:  The directory where the file is located.


        Description
        ~~~~~~~~~~~

        To search for the results file in the current working directory, set dir to None.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "bmrb.read("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", version=" + repr(version) + ")"
            print(text)

        # The argument checks.
        check.is_str(file, 'file name')
        check.is_str(dir, 'directory name', can_be_none=True)
        check.is_str(version, 'NMR-STAR dictionary version')

        # Execute the functional code.
        bmrb.read(file=file, directory=dir, version=version)


    def write(self, file=None, dir='pipe_name', version='3.1', force=False):
        """Write the results to a BMRB NMR-STAR formatted file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the BMRB file to output results to.  Optionally this can be a file
        object, or any object with a write() method.

        dir:  The directory name.

        version:  The NMR-STAR dictionary format version to use.
.sconsign.dblite
        force:  A flag which if True will cause the any pre-existing file to be overwritten.


        Description
        ~~~~~~~~~~~

        To place the BMRB file in the current working directory, set dir to None.  If dir is set
        to the special name 'pipe_name', then the results file will be placed into a directory with
        the same name as the current data pipe.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "bmrb.write("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", version=" + repr(version)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        check.is_str(file, 'file name')
        check.is_str(dir, 'directory name', can_be_none=True)
        check.is_str(version, 'NMR-STAR dictionary version')
        check.is_bool(force, 'force flag')

        # Execute the functional code.
        bmrb.write(file=file, directory=dir, version=version, force=force)
