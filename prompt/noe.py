###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
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

import sys

import help


class Noe:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for calculating NOE data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def read(self, run=None, file=None, dir=None, spectrum_type=None):
        """Function for reading peak intensities from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        file:  The name of the file containing the sequence data.

        dir:  The directory where the file is located.

        spectrum_type:  The type of spectrum.


        Description
        ~~~~~~~~~~~

        The spectrum_type argument can have the following values:
            'sat' - The NOE spectrum with proton saturation turned on.
            'ref' - The NOE reference spectrum.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "noe.read("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", spectrum_type=" + `spectrum_type` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The file name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The spectrum type.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        raise RelaxError, "Incomplete code."
