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


from Numeric import array
from os import F_OK, access
from cPickle import dump, load

from data import Data
from generic_functions import Generic_functions


class State(Generic_functions):
    def __init__(self, relax):
        """Class containing the functions for manipulating the program state."""

        self.relax = relax


    def load(self, file_name=None):
        """Function for loading a saved program state."""

        # Open file for reading.
        try:
            file = open(file_name, 'r')
        except IOError:
            print "The save file " + `file_name` + " does not exist."
            return

        # Reinitialise self.relax.data
        self.relax.data = Data()

        # Unpickle the data class.
        self.relax.data = load(file)

        # Close the file.
        file.close()


    def save(self, file_name=None, force=0):
        """Function for saving the program state."""

        # Open file for writing.
        if access(file_name, F_OK) and not force:
            print "The file " + `file_name` + " already exists.  Set the force flag to 1 to overwrite."
            return
        else:
            file = open(file_name, 'w')

        # Pickle the data class and write it to file
        dump(self.relax.data, file, 1)

        # Close the file.
        file.close()
