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


    def load(self, file=None, dir=None, compress_type=1):
        """Function for loading a saved program state."""

        # Open the file for reading.
        file = self.relax.IO.open_read_file(file_name=file, dir=dir, compress_type=compress_type)

        # Unpickle the data class.
        self.relax.data = load(file)

        # Close the file.
        file.close()


    def save(self, file=None, dir=None, force=0, compress_type=1):
        """Function for saving the program state."""

        # Open the file for writing.
        file = self.relax.IO.open_write_file(file_name=file, dir=dir, force=force, compress_type=compress_type)

        # Pickle the data class and write it to file
        dump(self.relax.data, file, 1)

        # Close the file.
        file.close()
