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


class Read:
    def __init__(self, relax):
        """Class containing functions for reading data from a file."""

        self.relax = relax


    def read(self, model=None, file=None):
        """Function for reading results from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the model.

        file:  The name of the file to read results from.
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "write("
            text = text + "model=" + `model`
            text = text + ", file=" + `file` + ")\n"
            print text

        # The model argument.
        if type(model) != str:
            print "The model argument " + `model` + " must be a string."
            return

        # File.
        if type(file) != str:
            print "The file name must be a string."
            return

        # Execute the functional code.
        self.relax.read.read_data(model=model, file=file)
