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

from bz2 import BZ2File
from gzip import GzipFile
from os import F_OK, access, makedirs, mkdir
from re import match, search
from string import split


class File_ops:
    def __init__(self, relax):
        """Class containing the file operations"""

        self.relax = relax


    def extract_data(self, file_name=None, dir=None, sep=None, compress_type=1):
        """Open the file 'file' and return all the data."""

        # File path.
        file_path = file_name
        if dir:
            file_path = dir + '/' + file_path

        # Test if the file exists and determine the compression type.
        if access(file_path, F_OK):
            compress_type = 0
            if search('.bz2$', file_path):
                compress_type = 1
            elif search('.gz$', file_path):
                compress_type = 2
        elif access(file_path + '.bz2', F_OK):
            file_path = file_path + '.bz2'
            compress_type = 1
        elif access(file_path + '.gz', F_OK):
            file_path = file_path + '.gz'
            compress_type = 2
        else:
            raise RelaxFileError, file_path

        # Open the file.
        try:
            print "Opening the file " + `file_path` + " for reading."
            if compress_type == 0:
                file = open(file_path, 'r')
            elif compress_type == 1:
                file = BZ2File(file_path, 'r')
            elif compress_type == 2:
                file = GzipFile(file_path, 'r')
        except IOError, message:
            raise RelaxError, "Cannot open the file " + `file_name` + ".  " + message.args[1] + "."


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


    def open_write_file(self, file_name=None, dir=None, force=0, compress_type=1):
        """Function for opening a file for writing and creating directories if necessary."""

        # Create the directories.
        if dir:
            try:
                makedirs(dir)
            except OSError:
                pass

        # File path.
        file_path = file_name
        if dir:
            file_path = dir + '/' + file_path
            if compress_type == 1 and not search('.bz2$', file_path):
                file_path = file_path + '.bz2'
            elif compress_type == 2 and not search('.gz$', file_path):
                file_path = file_path + '.gz'

        # Fail if the file already exists and the force flag is set to 0.
        if access(file_path, F_OK) and not force:
            raise RelaxFileOverwriteError, (file_path, 'force flag')

        # Open the file for writing.
        try:
            print "Opening the file " + `file_path` + " for writing."
            if compress_type == 0:
                file = open(file_path, 'w')
            elif compress_type == 1:
                file = BZ2File(file_path, 'w')
            elif compress_type == 2:
                file = GzipFile(file_path, 'w')
        except IOError, message:
            raise RelaxError, "Cannot open the file " + `file_path` + ".  " + message.args[1] + "."

        # Return the opened file.
        return file


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
