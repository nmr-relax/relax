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


from os import mkdir
from re import match
from string import split
import sys

class File_ops:
    def __init__(self, relax):
        """Class containing the file operations"""

        self.relax = relax


    def init_log_file(self, title='Log file'):
        """Initialise the log file."""

        self.relax.log = open('log.stage' + self.relax.data.stage, 'w')
        self.relax.log.write(title)


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
        for i in range(len(lines)):
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

        if self.relax.debug:
            self.relax.log.write("Making directory " + dir + "\n")
        try:
            mkdir(dir)
        except OSError:
            print "Directory ./" + dir + " already exists.\n"


#    #def read_file(self, file_name, message=''):
#    #    "Attempt to read the file, or quit the program if it does not exist."
#
#        try:
#            open(file_name, 'r')
#        except IOError:
#            print message
#            print "The file '" + file_name + "' does not exist, quitting program.\n\n\n"
#        file = open(file_name, 'r')
#        return file


#    def relax_data(self, file):
#        """Open the relaxation data in the file 'file' and return all the data.
#
#        It is assumed that the file has four columns separated by whitespace.  The columns should be:
#            0 - Residue numbers
#            1 - Residue names
#            2 - R1, R2, or NOE values
#            3 - The errors
#        """
#
#        lines = open(file, 'r')
#        lines = lines.readlines()
#        data = []
#        i = 0
#        for line in lines:
#            if i != 0:
#                j = i - 1
#                row = split(line)
#                data.append([])
#                data[j].append(row[0])
#                data[j].append(row[1])
#                data[j].append(float(row[2]))
#                data[j].append(float(row[3]))
#            i = i + 1
#        return data


    def strip(self, data):
        """Function to remove all comment and empty lines from the data data structure."""

        new = []
        for i in range(len(data)):
            if len(data[i]) == 0:
                continue
            elif match("#", data[i][0]):
                continue
            else:
                new.append(data[i])
        return new
