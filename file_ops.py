###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
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

from os import F_OK, access, makedirs, mkdir
from re import match
from string import split
import sys


class File_ops:
    def __init__(self, relax):
        """Class containing the file operations"""

        self.relax = relax


    def extract_data(self, file_name, sep=None):
        """Open the file 'file' and return all the data."""

        # Test if the file exists.
        try:
            file = open(file_name, 'r')
        except IOError:
            raise RelaxFileError, (None, file_name)

        # Create a data structure from the contents of the file split by either whitespace or the separator, sep.
        lines = file.readlines()
        data = []
        for i in xrange(len(lines)):
            if sep:
                row = split(lines[i], sep)
            else:
                row = split(lines[i])
            data.append(row)
        return data

        # Close the file.
        file.close()


    def mkdir(self, dir):
        """Create the given directory, or exit if the directory exists."""

        try:
            mkdir(dir)
        except OSError:
            print "Directory ./" + dir + " already exists.\n"


    def open_write_file(self, file, dir, force=0):
        """Function for opening a file for writing and creating directories if necessary."""

        # Create the directories.
        if dir:
            try:
                makedirs(dir)
            except OSError:
                pass

        # The file name.
        if dir:
            file_name = dir + '/' + file
        else:
            file_name = file

        # Fail if the file already exists and the force flag is set to 0.
        if access(file_name, F_OK) and not force:
            raise RelaxFileOverwriteError, (file_name, 'force flag')

        # Open the file for writing.
        open_file = open(file_name, 'w')

        # Return the opened file.
        return open_file


    def strip(self, data):
        """Function to remove all comment and empty lines from the data data structure."""

        new = []
        for i in xrange(len(data)):
            if len(data[i]) == 0:
                continue
            elif match("#", data[i][0]):
                continue
            else:
                new.append(data[i])
        return new
