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
        self.read = x.read
        self.rx_data = x.rx_data
        self.sequence = x.sequence


class Macro_class:
    def __init__(self, relax):
        """Class containing macros for loading data."""

        self.relax = relax
        self.rx_data = self.relax.rx_data.macro_read
        self.sequence = self.relax.sequence.macro_read


    def read(self, run=None, file=None, dir=None):
        """Function for reading results from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        file:  The name of the file to read results from.

        dir:  The directory where the file is located.
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "write("
            text = text + "run=" + `run`
            text = text + ", file=" + `file` + ")\n"
            text = text + ", dir=" + `dir` + ")\n"
            print text

        # The run argument.
        if type(run) != str:
            print "The run argument " + `run` + " must be a string."
            return

        # File.
        if type(file) != str:
            print "The file name must be a string."
            return

        # Directory.
        if dir != None or type(dir) != str:
            print "The directory name must be a string."
            return

        # Execute the functional code.
        self.relax.read.read_data(run=run, file=file, dir=dir)
