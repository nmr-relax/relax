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

from cPickle import dump, load


class State:
    def __init__(self, relax):
        """Class containing the functions for manipulating the program state."""

        self.relax = relax


    def load(self, file=None, dir=None):
        """Function for loading a saved program state."""

        # File path.
        if dir:
            file_path = dir + '/' + file
        else:
            file_path = file

        # Open file for reading.
        try:
            file = open(file_path, 'r')
        except IOError:
            raise RelaxFileError, ('save', file_path)

        # Unpickle the data class.
        self.relax.data = load(file)

        # Close the file.
        file.close()


    def save(self, file=None, dir=None, force=0):
        """Function for saving the program state."""

        # Open the file for writing.
        file = self.relax.file_ops.open_write_file(file, dir, force)

        # Pickle the data class and write it to file
        dump(self.relax.data, file, 1)

        # Close the file.
        file.close()
