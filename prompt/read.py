###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


class Read:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for loading data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def results(self, run=None, data_type=None, file='results', dir=None):
        """Function for reading results from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        data_type:  The type of data.

        file:  The name of the file to read results from.

        dir:  The directory where the file is located.


        Description
        ~~~~~~~~~~~

        The name of the run can be any string.

        The data_type argument specifies what type of data is to be read and must be one of the
        following:
            'mf' - model-free data.

        If no directory name is given, the results file will be searched for in a directory named
        after the run name.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "read.results("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The data_type argument.
        if type(data_type) != str:
            raise RelaxStrError, ('data_type', data_type)

        # File.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # Execute the functional code.
        self.__relax__.generic.rw.read_results(run=run, data_type=data_type, file=file, dir=dir)
