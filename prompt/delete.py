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


class Delete:
    def __init__(self, relax):
        """Class containing functions for writing data to a file."""

        self.relax = relax


    def delete(self, run=None, data_type=None):
        """Function for data removal.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        data_type:  The type of data to delete.


        Description
        ~~~~~~~~~~~

        The data_type argument specifies what type of data is to be deleted and must be one of the
        following:
            'seq' - sequence data.
            'rx_data' - relaxation data data.
            'mf' - model-free data.

        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "delete("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise UserArgStrError, ('run', run)

        # Data_type.
        if type(file) != str:
            raise UserArgStrError, ('file name', file)

        # Execute the functional code.
        self.relax.rw.write_data(run=run, file=file, dir=dir, force=force)
