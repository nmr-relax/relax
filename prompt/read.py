###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
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


class Skin:
    def __init__(self, relax):
        """The class accessible to the interpreter.

        The purpose of this class is to hide the variables and functions found within the namespace
        of the macro class, found below, except for those required for interactive use.  This is an
        abstraction layer designed to avoid user confusion as none of the macro class data
        structures are accessible.  For more flexibility use the macro class directly.
        """

        # Load the macro class into the namespace of this __init__ function.
        x = Macro_class(relax)

        # Place references to the interactive functions within the namespace of this skin class.
        self.read_data = x.read_data
        self.rx_data = x.rx_data
        self.sequence = x.sequence


class Macro_class:
    def __init__(self, relax):
        """Class containing macros for loading data."""

        self.relax = relax
        self.rx_data = self.relax.rx_data.macro_read
        self.sequence = self.relax.sequence.macro_read


    def read_data(self, run=None, data_type=None, file='results', dir=None):
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

        If no directory name is given, the results file will be seached for in a directory named
        after the run name.
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "read_data("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise UserArgStrError, ('run', run)

        # The data_type argument.
        if type(data_type) != str:
            raise UserArgStrError, ('data_type', data_type)

        # File.
        if type(file) != str:
            raise UserArgStrError, ('file name', file)

        # Directory.
        if dir != None:
            if type(dir) != str:
                raise UserArgNoneStrError, ('directory name', dir)

        # Execute the functional code.
        self.relax.rw.read_data(run=run, data_type=data_type, file=file, dir=dir)
