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

import __builtin__

# BZ2 compression module.
try:
    from bz2 import BZ2File
    __builtin__.bz2_module = 1
except ImportError, message:
    __builtin__.bz2_module = 0
    __builtin__.bz2_module_message = message.args[0]

# Gzip compression module.
from gzip import GzipFile

from os import F_OK, access, makedirs, mkdir, remove, stat
from os.path import expanduser
from re import match, search
from string import split


class File_ops:
    def __init__(self, relax):
        """Class containing the file operations"""

        self.relax = relax


    def delete(self, file_name=None, dir=None):
        """Function for deleting the given file."""

        # File path.
        file_path = file_name
        if dir:
            file_path = expanduser(dir + '/' + file_path)

        # Test if the file exists and determine the compression type.
        if access(file_path, F_OK):
            pass
        elif access(file_path + '.bz2', F_OK):
            file_path = file_path + '.bz2'
        elif access(file_path + '.gz', F_OK):
            file_path = file_path + '.gz'
        else:
            raise RelaxFileError, file_path

        # Remove the file.
        remove(file_path)


    def extract_data(self, file_name=None, dir=None, sep=None, compress_type=0):
        """Open the file 'file' and return all the data."""

        # Open the file.
        file = self.open_read_file(file_name=file_name, dir=dir, compress_type=compress_type)

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


    def open_read_file(self, file_name=None, dir=None, compress_type=0, print_flag=1):
        """Open the file 'file' and return all the data."""

        # File path.
        file_path = file_name
        if dir:
            file_path = expanduser(dir + '/' + file_path)

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

        # Open the file for reading.
        try:
            if print_flag:
                print "Opening the file " + `file_path` + " for reading."
            if compress_type == 0:
                file = open(file_path, 'r')
            elif compress_type == 1:
                if bz2_module:
                    file = BZ2File(file_path, 'r')
                else:
                    raise RelaxError, "Cannot open the file " + `file_path` + ", try uncompressing first.  " + bz2_module_message + "."
            elif compress_type == 2:
                file = GzipFile(file_path, 'r')
        except IOError, message:
            raise RelaxError, "Cannot open the file " + `file_path` + ".  " + message.args[1] + "."

        # Return the opened file.
        return file


    def open_write_file(self, file_name=None, dir=None, force=0, compress_type=0, print_flag=1):
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
            file_path = expanduser(dir + '/' + file_path)

        # File extension.
        if compress_type == 1 and not search('.bz2$', file_path):
            if bz2_module:
                file_path = file_path + '.bz2'
            else:
                print "Cannot use bz2 compression, using gzip compression instead.  " + bz2_module_message + "."
                file_path = file_path + '.gz'
        elif compress_type == 2 and not search('.gz$', file_path):
            file_path = file_path + '.gz'

        # Fail if the file already exists and the force flag is set to 0.
        if access(file_path, F_OK) and not force:
            raise RelaxFileOverwriteError, (file_path, 'force flag')

        # Open the file for writing.
        try:
            if print_flag:
                print "Opening the file " + `file_path` + " for writing."
            if compress_type == 0:
                file = open(file_path, 'w')
            elif compress_type == 1 and bz2_module:
                file = BZ2File(file_path, 'w')
            elif compress_type == 2 or not bz2_module:
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
