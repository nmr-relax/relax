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


class Delete:
    def __init__(self, relax):
        """Class for deleting data."""

        self.relax = relax


    def delete(self, run=None, data_type=None):
        """Function for deleting data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        data_type:  The type of data to delete.


        Description
        ~~~~~~~~~~~

        The 'run' argument can either a string or None.  If None, then the data corresponding to
        'data_type' for all runs will be deleted.

        The data_type argument specifies what type of data is to be deleted.  Only data
        corresponding to the run argument will be deleted.

        Valid data types include:
            None:  All data.
            res:  All residue specific data.
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "delete("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type` + ")"
            print text

        # The run argument.
        if run != None and type(run) != str:
            raise RelaxNoneStrError, ('run', run)

        # Data_type.
        if data_type != None and type(data_type) != str:
            raise RelaxNoneStrError, ('data type', data_type)

        # Execute the functional code.
        self.relax.generic.delete.data(run=run, data_type=data_type)
