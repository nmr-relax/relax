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

# Python module imports.
import sys

# relax module imports.
import help
from generic_fns import bmrb
from relax_errors import RelaxBoolError, RelaxIntError, RelaxNoneStrError, RelaxStrError, RelaxStrFileError


class BMRB:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for interfacing with the BMRB (http://www.bmrb.wisc.edu/)."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def display(self):
        """Display the BMRB data in NMR-STAR v3.1 format."""

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "bmrb.display("
            text = text + "format=" + `format` + ")"
            print text

        # Execute the functional code.
        bmrb.display(format=format)


    def read(self, file=None, dir=None):
        """Read BMRB files in the NMR-STAR v3.1 format.

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
            text = text + "file=" + `file`
            text = text + ", dir=" + `dir` + ")"
            print text

        # File.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # Execute the functional code.
        bmrb.read(file=file, directory=dir)


    def write(self, file=None, dir='pipe_name', force=False):
        """Write the results to a BMRB NMR-STAR v3.1 formatted file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the BMRB file to output results to.  Optionally this can be a file
        object, or any object with a write() method.

        dir:  The directory name.

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
            text = text + "file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

        # File.
        if type(file) != str and not hasattr(file, 'write'):
            raise RelaxStrFileError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != bool:
            raise RelaxBoolError, ('force flag', force)

        # Execute the functional code.
        bmrb.write(file=file, directory=dir, force=force)
