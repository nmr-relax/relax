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


class Write:
    def __init__(self, relax):
        """Class containing functions for writing data to a file."""

        self.relax = relax


    def write(self, run=None, file="results", dir=None, force=0):
        """Function for writing results to a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        file:  The name of the file to output results to.  The default is 'results'.

        dir:  The directory to place the results file in.

        force:  A flag which if set to 1 will cause the results file to be overwitten if it already
        exists.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the results file will be placed in a directory named after
        the run name.
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "write("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise UserError, "The run argument " + `run` + " must be a string."

        # File.
        if type(file) != str:
            raise UserError, "The file name must be a string."

        # Directory.
        if dir == None:
            pass
        elif type(dir) != str:
            raise UserError, "The directory name must be a string."

        # The force flag.
        if type(force) != int and force != 0 and force != 1:
            raise UserError, "The force flag should be the integer values of either 0 or 1."

        # Execute the functional code.
        self.relax.rw.write_data(run=run, file=file, dir=dir, force=force)
